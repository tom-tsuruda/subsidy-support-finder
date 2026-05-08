from django.db import models

# Create your models here.
from django.db import models


class SubsidyProgram(models.Model):
    STATUS_CHOICES = [
        ("open", "募集中"),
        ("scheduled", "予定"),
        ("closed", "終了"),
        ("unknown", "不明"),
    ]

    title = models.CharField("制度名", max_length=255)
    provider = models.CharField("実施機関", max_length=255, blank=True)
    area = models.CharField("対象地域", max_length=255, blank=True)
    target_business = models.TextField("対象者・対象事業者", blank=True)
    purpose_categories = models.JSONField("目的カテゴリ", default=list, blank=True)

    max_amount = models.CharField("補助上限額", max_length=100, blank=True)
    subsidy_rate = models.CharField("補助率", max_length=100, blank=True)

    application_start = models.DateField("公募開始日", null=True, blank=True)
    application_deadline = models.DateField("締切日", null=True, blank=True)

    status = models.CharField(
        "ステータス",
        max_length=50,
        choices=STATUS_CHOICES,
        default="open",
    )

    official_url = models.URLField("公式URL", blank=True)
    summary = models.TextField("概要", blank=True)
    consultant_comment = models.TextField("診断士コメント", blank=True)

    difficulty = models.IntegerField("申請難易度", default=3)
    recommendation_score = models.IntegerField("おすすめ度", default=3)
    is_active = models.BooleanField("有効", default=True)

    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        verbose_name = "補助金・支援策"
        verbose_name_plural = "補助金・支援策"

    def __str__(self):
        return self.title