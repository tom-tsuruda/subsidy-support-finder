from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Inquiry


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "company_name",
        "email",
        "diagnosis_interest",
        "created_at",
        "is_handled",
    )
    list_filter = ("is_handled", "created_at")
    search_fields = (
        "company_name",
        "name",
        "email",
        "message",
        "diagnosis_area",
        "diagnosis_industry",
        "diagnosis_interest",
    )
    readonly_fields = ("created_at",)