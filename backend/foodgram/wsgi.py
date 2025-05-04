import os
from django.core.wsgi import get_wsgi_application

# Задаём настройки для работы с WSGI сервером
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')

application = get_wsgi_application()
