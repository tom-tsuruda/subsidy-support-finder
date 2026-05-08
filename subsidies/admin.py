from django.contrib import admin
from .models import SubsidyProgram


@admin.register(SubsidyProgram)
class SubsidyProgramAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "provider",
        "area",
        "status",
        "application_deadline",
        "recommendation_score",
        "is_active",
    )
    list_filter = ("status", "is_active", "area")
    search_fields = ("title", "provider", "area", "summary", "consultant_comment")