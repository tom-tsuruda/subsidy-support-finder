import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from django.utils import timezone

from subsidies.models import SubsidyProgram


JNET21_URL = "https://j-net21.smrj.go.jp/snavi2/results.php"


def fetch_html_with_retry(url, headers, retries=3, timeout=30, wait_seconds=3):
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            return response.text
        except requests.exceptions.RequestException as e:
            last_error = e
            print(f"J-Net21取得失敗 {attempt}/{retries}: {e}")
            if attempt < retries:
                time.sleep(wait_seconds)

    raise last_error


def fetch_jnet21_subsidies():
    """
    J-Net21 支援情報ヘッドラインから補助金・助成金系の情報を取得する。
    まずは一覧ページ内のリンクから制度情報らしいものを保存する。
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }

    html = fetch_html_with_retry(
        JNET21_URL,
        headers=headers,
        retries=3,
        timeout=30,
        wait_seconds=3,
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

        keywords = ["補助金", "助成金", "融資", "支援", "公募", "募集"]
        if not any(keyword in title for keyword in keywords):
            continue

        source_url = urljoin(JNET21_URL, href)

        obj, created = SubsidyProgram.objects.update_or_create(
            source_url=source_url,
            defaults={
                "title": title[:255],
                "provider": "J-Net21",
                "area": "",
                "summary": title,
                "official_url": source_url,
                "source_name": "J-Net21",
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
        "source": "J-Net21",
        "created": created_count,
        "updated": updated_count,
    }