docker-compose down -v --remove-orphans

docker-compose up -d --build

docker-compose exec backend python manage.py migrate

docker-compose exec backend python manage.py load_ingredients

docker-compose exec backend python manage.py createsuperuser
