# Foodgram

Это сервис для публикации и обмена кулинарными рецептами. 

Пользователи могут создавать новые рецепты, просматривать чужие, отмечать любимые и скачивать список необходимых ингредиентов.

## Технологии

- Python
- Django REST Framework
- PostgreSQL
- Docker & Docker Compose

## Запуск

### Предварительные требования

- Установлён Docker Compose  

### Клонирование репозитория

```bash
git clone git@github.com:vadimbelan/foodgram-st.git
cd foodgram-st
```
### Настройка переменных окружения

Создайте файл .env в корне проекта со следующим содержимым:

```bash
cat > .env <<EOF
DB_HOST=db
DB_PORT=5432
POSTGRES_USER=foodgram
POSTGRES_PASSWORD=foodgram
POSTGRES_DB=foodgram
ALLOWED_HOSTS=localhost,127.0.0.1,backend
CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1
EOF
```

### Запуск контейнеров

```bash
docker-compose down -v --remove-orphans
docker-compose up -d --build
```

### Первоначальная настройка проекта

```bash
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py load_ingredients
docker-compose exec backend python manage.py collectstatic
docker-compose exec backend python manage.py createsuperuser
```

## Доступ к проекту

Главная страница: [Foodgram](http://localhost)

Админ-панель: [Foodgram Admin](http://localhost/admin)

API-документация: [Foodgram API](http://localhost/api)

## Контакты

[Белан Вадим](mailto:s21380403@unn.ru)

## Замечания (Строка - комментарий)

### api/serializers.py:

- **96.** Лишняя переменная, так как одноразовая.

- **97.** Рекомендую такое оформление:
  ```python
  self.context["request"].GET.get("recipes_limit", 10**10)
  ```

### api/views.py:

- **65.** Рано! Для поиска в строке 69 не нужен рецепт как ORM-запись.  
  Достаточно только его ключа, то есть `pk`.

- **78.** Из модели извлеките её русское название и добавьте в описание проблемы.

- **158.** Лишняя строка.

- **230.** Рано! Для поиска в строке 238 не нужен автор — достаточно его ключа `id`.

- **233.** Перенесите две строки под строку 242.

### recipes/management/commands/load_ingredients.py:

- **17.** Лишняя переменная, так как одноразовая.

- **24.** Лишняя переменная, так как одноразовая.

- **34.** Перенесите строки 24..34 внутрь `try`.

### recipes/models.py:

- **12.** Это не "имя"! Имя — в следующем поле.

- **52.** Обманывающий комментарий хуже, чем код без комментария.  
  Это элементы подписок для авторов.

- **97.** Ого! А рисунок нельзя будет приложить?

- **164.** Рекомендую заменить `%(class)s_relations` на `%(class)ss`.

- **182.** Лишнее поле.

- **195.** Лишнее поле.

### recipes/admin.py:

- **4.** Лишняя строка. Применяйте только `mark_safe`.  
  Лучше использовать не функцию, а декоратор.

### recipes/views.py:

- **11.** Обязательно включайте в описание проблемы важные детали.  
  Здесь — значение, из-за которого остановлена работа. Какой рецепт?

- **13.** Лишний код `api/`.

### README.md:

- **64.** Ошибка "не по ТЗ".  
  Должен быть URL `api/docs/`.
