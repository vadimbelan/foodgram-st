import os
from django.core.asgi import get_asgi_application

# Настройка для работы с асинхронным сервером.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings')

application = get_asgi_application()
