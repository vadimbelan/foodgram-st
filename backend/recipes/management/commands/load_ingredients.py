import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Импортирует продукты из JSON‑файла в базу"

    def handle(self, *args, **options):
        file_path = Path(settings.BASE_DIR) / "data" / "ingredients.json"

        try:
            records = json.loads(file_path.read_text(encoding="utf-8"))
        except Exception as exc:
            self.stderr.write(
                self.style.ERROR(f"Не удалось прочитать {file_path.name}: {exc}")
            )
            return

        before = Ingredient.objects.count()
        objs = [Ingredient(**rec) for rec in records]
        # ignore_conflicts=True не останавливает импорт при дублях
        created = Ingredient.objects.bulk_create(objs, ignore_conflicts=True)
        added = len(created)
        total = Ingredient.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f"Импорт завершён: добавлено {added}, всего продуктов {total}"
            )
        )
