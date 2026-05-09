from django.core.management.base import BaseCommand

from subsidies.scrapers.jnet21 import fetch_jnet21_subsidies


class Command(BaseCommand):
    help = "Fetch subsidy information from official sources"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("補助金情報の取得を開始します..."))

        scrapers = [
            ("J-Net21", fetch_jnet21_subsidies),
        ]

        results = []

        for name, scraper in scrapers:
            try:
                self.stdout.write(self.style.NOTICE(f"{name} の取得を開始します..."))
                result = scraper()
                results.append(result)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"{name} の取得でエラー: {e}"))

        for result in results:
            self.stdout.write(
                self.style.SUCCESS(
                    f"{result['source']}: 新規 {result['created']} 件 / 更新 {result['updated']} 件"
                )
            )

        self.stdout.write(self.style.SUCCESS("補助金情報の取得が完了しました。"))