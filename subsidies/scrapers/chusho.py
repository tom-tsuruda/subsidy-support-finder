import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from django.utils import timezone

from subsidies.models import SubsidyProgram


CHUSHO_KOBO_URL = "https://www.chusho.meti.go.jp/koukai/hojyokin/kobo.html"


def fetch_html_with_retry(url, headers, retries=3, timeout=60, wait_seconds=5):
    """
    外部サイト取得用の共通処理。
    タイムアウトや一時的な接続失敗に備えてリトライする。
    """
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            return response.text
        except requests.exceptions.RequestException as e:
            last_error = e
            print(f"取得失敗 {attempt}/{retries}: {e}")
            if attempt < retries:
                time.sleep(wait_seconds)

    raise last_error


def fetch_chusho_subsidies():
    """
    中小企業庁の補助金公募情報ページから補助金情報を取得する。
    現在の SubsidyProgram モデルに合わせた保存処理。
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }

    html = fetch_html_with_retry(
        CHUSHO_KOBO_URL,
        headers=headers,
        retries=3,
        timeout=60,
        wait_seconds=5,
    )

    soup = BeautifulSoup(html, "lxml")

    created_count = 0
    updated_count = 0

    links = soup.find_all("a")

    for link in links:
        title = link.get_text(strip=True)
        href = link.get("href")

        if not title or not href:
            continue

        keywords = ["補助金", "公募", "助成", "支援", "交付"]
        if not any(keyword in title for keyword in keywords):
            continue

        source_url = urljoin(CHUSHO_KOBO_URL, href)

        obj, created = SubsidyProgram.objects.update_or_create(
            source_url=source_url,
            defaults={
                "title": title[:255],
                "provider": "中小企業庁",
                "area": "全国",
                "summary": title,
                "official_url": source_url,
                "source_name": "中小企業庁",
                "fetched_at": timezone.now(),
                "raw_text": title,
                "status": "unknown",
                "is_active": True,
            },
        )

        if created:
            created_count += 1
        else:
            updated_count += 1

    return {
        "source": "中小企業庁",
        "created": created_count,
        "updated": updated_count,
    }