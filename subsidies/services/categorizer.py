def guess_purpose_categories(text):
    """
    補助金・支援策のタイトルや概要から、目的カテゴリを推定する。
    最初はシンプルなキーワード判定で十分。
    """
    categories = []

    keyword_map = {
        "it": [
            "IT",
            "ＤＸ",
            "DX",
            "デジタル",
            "システム",
            "ソフトウェア",
            "クラウド",
            "AI",
            "IoT",
            "業務効率化",
        ],
        "equipment": [
            "設備",
            "機械",
            "装置",
            "省力化",
            "生産性向上",
            "自動化",
            "ロボット",
        ],
        "sales": [
            "販路",
            "販売促進",
            "展示会",
            "商談会",
            "広告",
            "宣伝",
            "ホームページ",
            "EC",
            "海外展開",
        ],
        "energy": [
            "省エネ",
            "脱炭素",
            "再エネ",
            "カーボンニュートラル",
            "CO2",
            "環境",
        ],
        "startup": [
            "創業",
            "起業",
            "スタートアップ",
            "新規開業",
        ],
        "business_successor": [
            "事業承継",
            "後継者",
            "M&A",
        ],
        "wage": [
            "賃上げ",
            "最低賃金",
            "人材確保",
            "雇用",
            "採用",
        ],
        "finance": [
            "融資",
            "資金繰り",
            "貸付",
            "信用保証",
            "利子補給",
        ],
    }

    for category, keywords in keyword_map.items():
        if any(keyword in text for keyword in keywords):
            categories.append(category)

    if not categories:
        categories.append("subsidy")

    return categories