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
            raw = file_path.read_text(encoding="utf-8")
            for record in json.loads(raw):
                Ingredient.objects.get_or_create(**record)
        except Exception as exc:
            self.stderr.write(
                self.style.ERROR(f"Импорт из {file_path.name} не выполнен: {exc}")
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Импорт из {file_path.name} завершён. Всего продуктов: {Ingredient.objects.count()}"
            )
        )
