import requests
from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand
from django.utils import timezone

from subsidies.models import SubsidyProgram
from subsidies.services.categorizer import guess_purpose_categories

class Command(BaseCommand):
    help = "Fetch subsidy programs from J-Net21"

    def handle(self, *args, **options):
        self.stdout.write("J-Net21から補助金・支援策データの取得を開始します。")

        url = "https://j-net21.smrj.go.jp/snavi2/results.php"

        params = {
            "keyword": "",
        }

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        }

        try:
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=20,
            )
            response.raise_for_status()
        except requests.RequestException as e:
            self.stderr.write(self.style.ERROR(f"取得エラー: {e}"))
            return

        soup = BeautifulSoup(response.text, "html.parser")

        # まずはページ全体のテキストを確認用に使う
        page_text = soup.get_text("\n", strip=True)

        # J-Net21の検索結果では、h3に制度名が入っているケースが多い
        headings = soup.find_all(["h3", "h2"])

        created_count = 0
        updated_count = 0

        for heading in headings:
            title = heading.get_text(" ", strip=True)

            if not title:
                continue

            # 明らかに検索フォーム系・見出し系の文言は除外
            skip_words = [
                "条件を指定して検索",
                "現在の検索条件",
                "検索結果一覧",
                "カテゴリ",
                "キーワード",
            ]

            if any(word in title for word in skip_words):
                continue

            # 補助金・助成金っぽいものだけ残す
            target_words = [
                "補助金",
                "助成金",
                "支援",
                "融資",
                "給付",
                "公募",
            ]

            if not any(word in title for word in target_words):
                continue

            link_tag = heading.find("a")
            detail_url = url

            if link_tag and link_tag.get("href"):
                href = link_tag.get("href")
                detail_url = requests.compat.urljoin(url, href)

            raw_text = title
            purpose_categories = guess_purpose_categories(raw_text)
            program, created = SubsidyProgram.objects.update_or_create(
                title=title,
                source_url=detail_url,
                defaults={
                    "provider": "",
                    "area": "全国",
                    "target_business": "中小企業・小規模事業者",
                    "purpose_categories": purpose_categories,
                    "status": "unknown",
                    "official_url": detail_url,
                    "source_name": "J-Net21 支援情報ヘッドライン",
                    "fetched_at": timezone.now(),
                    "summary": title,
                    "raw_text": raw_text,
                    "is_active": True,
                },
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"取得完了：新規 {created_count} 件、更新 {updated_count} 件"
            )
        )