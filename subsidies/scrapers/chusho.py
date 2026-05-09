import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

from subsidies.models import Subsidy


CHUSHO_KOBO_URL = "https://www.chusho.meti.go.jp/koukai/hojyokin/kobo.html"


def fetch_chusho_subsidies():
    """
    中小企業庁の補助金公募情報ページから補助金情報を取得する。
    まずはタイトル・URL・取得元を保存する最小構成。
    """

    headers = {
        "User-Agent": "subsidy-support-finder/0.1 (+https://your-website.example.com)"
    }

    response = requests.get(CHUSHO_KOBO_URL, headers=headers, timeout=20)
    response.raise_for_status()
    response.encoding = response.apparent_encoding

    soup = BeautifulSoup(response.text, "lxml")

    created_count = 0
    updated_count = 0

    # 中小企業庁ページ内のリンクを広めに取得
    links = soup.find_all("a")

    for link in links:
        title = link.get_text(strip=True)
        href = link.get("href")

        if not title or not href:
            continue

        # 補助金・公募っぽいものだけ残す
        keywords = ["補助金", "公募", "助成", "支援", "交付"]
        if not any(keyword in title for keyword in keywords):
            continue

        source_url = urljoin(CHUSHO_KOBO_URL, href)

        obj, created = Subsidy.objects.update_or_create(
            source_url=source_url,
            defaults={
                "title": title[:255],
                "summary": title,
                "organization": "中小企業庁",
                "source_name": "中小企業庁",
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