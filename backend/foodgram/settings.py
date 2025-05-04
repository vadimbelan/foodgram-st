import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Путь к корневой директории проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Открытые переменные конфигурации
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
DEBUG = os.getenv("DEBUG", "True") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Приложения
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",

    "api",
    "users",
    "recipes",
    "djoser",
]

# Middleware для обработки запросов
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "foodgram.urls"

# Настройки для шаблонов
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "foodgram.wsgi.application"

# Настройки базы данных
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "foodgram_db"),
        "USER": os.getenv("POSTGRES_USER", "user"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", 5432),
    }
}

# Валидаторы паролей
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Международная настройка
LANGUAGE_CODE = "ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True

# Статические и медиа файлы
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Пользовательская модель
AUTH_USER_MODEL = "users.UserProfile"

# Настройки для DRF
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_PAGINATION_CLASS": "api.pagination.CustomPagination",
    "PAGE_SIZE": 6,
}

DJOSER = {
    "SERIALIZERS": {
        "user_create": "djoser.serializers.UserCreateSerializer",
        "user": "api.serializers.PublicUserSerializer",
        "current_user": "api.serializers.PublicUserSerializer",
    },
    "PERMISSIONS": {
        "user": ["djoser.permissions.CurrentUserOrAdminOrReadOnly"],
        "user_list": ["rest_framework.permissions.IsAuthenticatedOrReadOnly"],
    },
    "HIDE_USERS": False,
}

# Доверенные Origin’ы для CSRF (схема://хост[:порт])
CSRF_TRUSTED_ORIGINS = os.getenv(
    "CSRF_TRUSTED_ORIGINS",
    "http://localhost,http://127.0.0.1"
).split(",")
