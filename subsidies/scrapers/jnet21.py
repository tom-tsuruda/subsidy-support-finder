import hashlib
import re
import time
from datetime import date
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from django.utils import timezone

from subsidies.models import SubsidyProgram


JNET21_SEARCH_URL = "https://j-net21.smrj.go.jp/snavi2/results.php"

# J-Net21 prefecture code. 00 is nationwide.
# 初期運用では「全国」を厚めに取り、近畿・東京・愛知も少し拾う。
SEARCH_TARGETS = [
    {"label": "全国", "prefecture_code": "00", "pages": 4},
    {"label": "大阪府", "prefecture_code": "27", "pages": 2},
    {"label": "京都府", "prefecture_code": "26", "pages": 1},
    {"label": "兵庫県", "prefecture_code": "28", "pages": 1},
    {"label": "滋賀県", "prefecture_code": "25", "pages": 1},
    {"label": "奈良県", "prefecture_code": "29", "pages": 1},
    {"label": "和歌山県", "prefecture_code": "30", "pages": 1},
    {"label": "東京都", "prefecture_code": "13", "pages": 1},
    {"label": "愛知県", "prefecture_code": "23", "pages": 1},
]


PURPOSE_KEYWORDS = {
    "it": ["IT", "ＤＸ", "DX", "デジタル", "システム", "ソフトウェア", "省力化", "生産性"],
    "equipment": ["設備", "機械", "装置", "導入", "投資", "省力化"],
    "sales": ["販路", "販売", "展示会", "商談", "マーケティング", "海外展開"],
    "energy": ["省エネ", "脱炭素", "再エネ", "環境", "SDGs", "カーボン"],
    "startup": ["創業", "起業", "スタートアップ", "新規就農"],
    "business_successor": ["事業承継", "M&A", "後継者", "承継"],
    "wage": ["賃上げ", "雇用", "人材", "採用", "リスキリング", "育成"],
    "finance": ["融資", "貸付", "資金", "保証", "利子", "経営改善"],
}


DATE_PATTERN = re.compile(r"(20\d{2})年(\d{1,2})月(\d{1,2})日")


def fetch_html_with_retry(url, headers, params=None, retries=3, timeout=30, wait_seconds=2):
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            return response.text, response.url
        except requests.exceptions.RequestException as e:
            last_error = e
            print(f"J-Net21取得失敗 {attempt}/{retries}: {e}")
            if attempt < retries:
                time.sleep(wait_seconds)

    raise last_error


def normalize_text(value):
    return re.sub(r"\s+", " ", value or "").strip()


def parse_japanese_date(value):
    match = DATE_PATTERN.search(value or "")
    if not match:
        return None

    year, month, day = map(int, match.groups())
    try:
        return date(year, month, day)
    except ValueError:
        return None


def parse_period(period_text):
    dates = DATE_PATTERN.findall(period_text or "")

    if not dates:
        return None, None

    parsed_dates = []
    for year, month, day in dates:
        try:
            parsed_dates.append(date(int(year), int(month), int(day)))
        except ValueError:
            continue

    if not parsed_dates:
        return None, None

    if "～" in period_text and period_text.strip().startswith("～"):
        return None, parsed_dates[0]

    if len(parsed_dates) == 1:
        return None, parsed_dates[0]

    return parsed_dates[0], parsed_dates[-1]


def extract_field(block_text, label):
    pattern = rf"{re.escape(label)}：\s*(.*?)(?=\s*(実施機関|募集期間)：|$)"
    match = re.search(pattern, block_text, flags=re.DOTALL)
    if not match:
        return ""
    return normalize_text(match.group(1))


def infer_purpose_categories(text):
    categories = []

    for category, keywords in PURPOSE_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            categories.append(category)

    return categories


def infer_status(deadline):
    if not deadline:
        return "unknown"

    if deadline >= timezone.localdate():
        return "open"

    return "closed"


def build_search_params(prefecture_code, page):
    return {
        "category": "2",  # 補助金・助成金・融資
        "prefecture[]": prefecture_code,
        "displaycount": "30",
        "displaysort": "DESC",
        "sort": "publish_date_default",
        "search_exec": "1",
        "page": str(page),
    }


def make_fallback_url(page_url, title, provider, area):
    key = f"{page_url}|{title}|{provider}|{area}"
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]
    return f"{page_url}#program-{digest}"


def parse_result_blocks(html, page_url):
    soup = BeautifulSoup(html, "lxml")
    results = []

    for heading in soup.find_all(["h3", "h2"]):
        title = normalize_text(heading.get_text(" ", strip=True))

        if not title:
            continue

        if not any(keyword in title for keyword in ["補助金", "助成金", "融資", "貸付", "支援"]):
            continue

        container = heading.find_parent("li") or heading.find_parent("article") or heading.parent
        block_text = normalize_text(container.get_text(" ", strip=True) if container else title)

        provider = extract_field(block_text, "実施機関")
        period_text = extract_field(block_text, "募集期間")
        application_start, application_deadline = parse_period(period_text)

        published_at = parse_japanese_date(block_text)

        area = ""
        if published_at:
            date_text = f"{published_at.year}年{published_at.month}月{published_at.day}日"
            after_date = block_text.split(date_text, 1)
            if len(after_date) == 2:
                area_candidate = after_date[1].split("お気に入り登録", 1)[0]
                area = normalize_text(area_candidate)

        if not area:
            area_match = re.search(r"20\d{2}年\d{1,2}月\d{1,2}日\s+([^\s]+)", block_text)
            if area_match:
                area = normalize_text(area_match.group(1))

        link_tag = heading.find("a") or (container.find("a") if container else None)
        href = link_tag.get("href") if link_tag else ""
        official_url = urljoin(page_url, href) if href else ""
        source_url = official_url or make_fallback_url(page_url, title, provider, area)

        purpose_categories = infer_purpose_categories(f"{title} {block_text}")

        results.append({
            "title": title[:255],
            "provider": provider or "未取得",
            "area": area or "未取得",
            "summary": block_text,
            "official_url": official_url or page_url,
            "source_url": source_url,
            "source_name": "J-Net21検索",
            "application_start": application_start,
            "application_deadline": application_deadline,
            "purpose_categories": purpose_categories,
            "raw_text": block_text,
            "status": infer_status(application_deadline),
            "is_active": True,
        })

    return results


def save_or_update_program(source_url, defaults):
    existing = SubsidyProgram.objects.filter(source_url=source_url).order_by("id").first()

    if existing:
        for key, value in defaults.items():
            setattr(existing, key, value)
        existing.save()
        return existing, False

    obj = SubsidyProgram.objects.create(source_url=source_url, **defaults)
    return obj, True


def fetch_jnet21_subsidies():
    """
    J-Net21 支援情報ヘッドラインの検索結果ページから、
    対象地域・実施機関・募集期間・目的カテゴリを含めて取得する。
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }

    created_count = 0
    updated_count = 0
    parsed_count = 0

    for target in SEARCH_TARGETS:
        label = target["label"]
        prefecture_code = target["prefecture_code"]
        pages = target["pages"]

        for page in range(1, pages + 1):
            params = build_search_params(prefecture_code, page)
            html, page_url = fetch_html_with_retry(
                JNET21_SEARCH_URL,
                headers=headers,
                params=params,
                retries=3,
                timeout=30,
                wait_seconds=2,
            )

            programs = parse_result_blocks(html, page_url)
            print(f"J-Net21検索: {label} page {page} / {len(programs)}件解析")

            if not programs:
                break

            for program in programs:
                source_url = program.pop("source_url")
                program["fetched_at"] = timezone.now()

                obj, created = save_or_update_program(source_url, program)
                parsed_count += 1

                if created:
                    created_count += 1
                else:
                    updated_count += 1

            time.sleep(0.5)

    return {
        "source": "J-Net21検索",
        "created": created_count,
        "updated": updated_count,
        "parsed": parsed_count,
    }