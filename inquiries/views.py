from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect

from .models import Inquiry


def contact_form(request):
    if request.method == "POST":
        inquiry = Inquiry.objects.create(
            company_name=request.POST.get("company_name", "").strip(),
            name=request.POST.get("name", "").strip(),
            email=request.POST.get("email", "").strip(),
            message=request.POST.get("message", "").strip(),
            diagnosis_area=request.POST.get("diagnosis_area", "").strip(),
            diagnosis_industry=request.POST.get("diagnosis_industry", "").strip(),
            diagnosis_interest=request.POST.get("diagnosis_interest", "").strip(),
            diagnosis_programs=request.POST.get("diagnosis_programs", "").strip(),
        )

        subject = "【補助金・支援策診断】新しい問い合わせがありました"

        body = f"""
補助金・支援策診断から新しい問い合わせがありました。

【会社名・屋号】
{inquiry.company_name}

【お名前】
{inquiry.name}

【メールアドレス】
{inquiry.email}

【相談内容】
{inquiry.message}

【診断時の所在地】
{inquiry.diagnosis_area}

【診断時の業種】
{inquiry.diagnosis_industry}

【診断時の検討内容】
{inquiry.diagnosis_interest}

【候補となった支援策】
{inquiry.diagnosis_programs}

管理画面で確認してください。
"""

        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_NOTIFICATION_EMAIL],
            fail_silently=False,
        )

        return redirect("inquiries:contact_thanks")

    context = {
        "diagnosis_area": request.GET.get("area", ""),
        "diagnosis_industry": request.GET.get("industry", ""),
        "diagnosis_interest": request.GET.get("interest", ""),
        "diagnosis_programs": request.GET.get("programs", ""),
    }

    return render(request, "inquiries/contact_form.html", context)


def contact_thanks(request):
    return render(request, "inquiries/contact_thanks.html")