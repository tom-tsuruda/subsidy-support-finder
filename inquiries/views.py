from django.shortcuts import render, redirect
from .models import Inquiry


def contact_form(request):
    if request.method == "POST":
        Inquiry.objects.create(
            company_name=request.POST.get("company_name", "").strip(),
            name=request.POST.get("name", "").strip(),
            email=request.POST.get("email", "").strip(),
            message=request.POST.get("message", "").strip(),
            diagnosis_area=request.POST.get("diagnosis_area", "").strip(),
            diagnosis_industry=request.POST.get("diagnosis_industry", "").strip(),
            diagnosis_interest=request.POST.get("diagnosis_interest", "").strip(),
        )

        return redirect("inquiries:contact_thanks")

    return render(request, "inquiries/contact_form.html")


def contact_thanks(request):
    return render(request, "inquiries/contact_thanks.html")