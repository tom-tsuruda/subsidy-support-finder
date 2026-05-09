from django.db import models

# Create your models here.
from django.db import models


class Inquiry(models.Model):
    company_name = models.CharField("会社名・屋号", max_length=255, blank=True)
    name = models.CharField("お名前", max_length=100)
    email = models.EmailField("メールアドレス")
    message = models.TextField("相談内容")

    diagnosis_area = models.CharField("診断時の所在地", max_length=100, blank=True)
    diagnosis_industry = models.CharField("診断時の業種", max_length=100, blank=True)
    diagnosis_interest = models.CharField("診断時の検討内容", max_length=255, blank=True)

    created_at = models.DateTimeField("送信日時", auto_now_add=True)
    is_handled = models.BooleanField("対応済み", default=False)

    class Meta:
        verbose_name = "問い合わせ"
        verbose_name_plural = "問い合わせ"

    def __str__(self):
        return f"{self.name} - {self.email}"