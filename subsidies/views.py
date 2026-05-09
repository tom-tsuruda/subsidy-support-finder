from django.shortcuts import render, get_object_or_404
from .models import SubsidyProgram


INTEREST_LABELS = {
    "it": "ITツールを導入したい",
    "equipment": "設備投資をしたい",
    "sales": "販路開拓をしたい",
    "energy": "省エネに取り組みたい",
    "startup": "創業したい",
    "business_successor": "事業承継を考えている",
    "wage": "賃上げ・人材確保をしたい",
    "finance": "資金繰りを改善したい",
}


def diagnosis_form(request):
    if request.method == "POST":
        area = request.POST.get("area", "").strip()
        industry = request.POST.get("industry", "").strip()
        employee_count = request.POST.get("employee_count", "").strip()
        business_type = request.POST.get("business_type", "").strip()
        interest = request.POST.get("interest", "").strip()
        investment_amount = request.POST.get("investment_amount", "").strip()

        programs = SubsidyProgram.objects.filter(
            is_active=True,
            status__in=["open", "scheduled", "unknown"],
        ).exclude(
            provider__in=["", "未取得"]
        ).exclude(
            area__in=["", "未取得"]
        ).exclude(
            title__icontains="一覧"
        ).exclude(
            title__icontains="検索"
        ).exclude(
            title__icontains="まとめ"
        )

        matched_programs = []

        for program in programs:
            score = 0

            # 地域判定
            # 地域判定
            # 地域判定
            if area:
                if program.area == "全国" or area in program.area or program.area in area:
                    score += 5
                else:
                    continue

            # 目的カテゴリ判定
            if interest and interest in program.purpose_categories:
                score += 10

            # タイトル・概要にも選択内容に近い文字があれば軽く加点
            interest_label = INTEREST_LABELS.get(interest, "")
            text_for_search = f"{program.title} {program.summary} {program.raw_text}"

            if interest_label:
                for word in interest_label.replace("・", " ").split():
                    if word and word in text_for_search:
                        score += 1

            # おすすめ度
            score += min(program.recommendation_score, 3)

            if score >= 12:
                match_label = "高"
                match_stars = "★★★★★"
            elif score >= 8:
                match_label = "中"
                match_stars = "★★★★☆"
            elif score >= 5:
                match_label = "やや低"
                match_stars = "★★★☆☆"
            else:
                match_label = "参考"
                match_stars = "★★☆☆☆"

            if score > 0:
                matched_programs.append({
                    "program": program,
                    "score": score,
                    "match_label": match_label,
                    "match_stars": match_stars,
                })

        matched_programs = sorted(
            matched_programs,
            key=lambda x: x["score"],
            reverse=True,
        )

        context = {
            "area": area,
            "industry": industry,
            "employee_count": employee_count,
            "business_type": business_type,
            "interest": interest,
            "interest_label": INTEREST_LABELS.get(interest, interest),
            "investment_amount": investment_amount,
            "matched_programs": matched_programs[:20],
        }

        return render(request, "subsidies/diagnosis_result.html", context)

    return render(
        request,
        "subsidies/diagnosis_form.html",
        {"interest_labels": INTEREST_LABELS},
    )

def program_detail(request, pk):
    program = get_object_or_404(
        SubsidyProgram,
        pk=pk,
        is_active=True,
    )

    return render(
        request,
        "subsidies/program_detail.html",
        {"program": program},
    )