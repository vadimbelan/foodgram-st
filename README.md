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
DB_HOST=db
DB_PORT=5432
POSTGRES_USER=foodgram
POSTGRES_PASSWORD=foodgram
POSTGRES_DB=foodgram
ALLOWED_HOSTS=localhost,127.0.0.1,backend
CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1
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
docker-compose exec backend python manage.py createsuperuser
```

После запуска сервис доступен по адресу http://localhost
