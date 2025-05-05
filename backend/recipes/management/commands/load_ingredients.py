import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импортирует ингредиенты из JSON‑файла в базу данных'

    def handle(self, *args, **options):
        # Формируем путь к файлу
        json_path = Path(settings.BASE_DIR) / 'data' / 'ingredients.json'

        # Проверяем существование
        if not json_path.exists():
            self.stderr.write(self.style.ERROR(f'Не найден файл: {json_path}'))
            return

        # Читаем и разбираем JSON
        try:
            raw = json_path.read_text(encoding='utf-8')
            items = json.loads(raw)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Ошибка при чтении JSON: {e}'))
            return

        # Подготавливаем объекты и сохраняем одним запросом
        objs = [Ingredient(**data) for data in items]
        created = Ingredient.objects.bulk_create(objs)

        # Выводим результат
        count = len(created)
        self.stdout.write(
            self.style.SUCCESS(
                f"Загружено {count} ингредиентов."
            )
        )
