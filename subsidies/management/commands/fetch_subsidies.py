from django.core.management.base import BaseCommand

from subsidies.scrapers.chusho import fetch_chusho_subsidies


class Command(BaseCommand):
    help = "Fetch subsidy information from multiple official sources"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("補助金情報の取得を開始します..."))

        results = []

        try:
            results.append(fetch_chusho_subsidies())
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"中小企業庁の取得でエラー: {e}"))

        for result in results:
            self.stdout.write(
                self.style.SUCCESS(
                    f"{result['source']}: 新規 {result['created']} 件 / 更新 {result['updated']} 件"
                )
            )

        self.stdout.write(self.style.SUCCESS("補助金情報の取得が完了しました。"))