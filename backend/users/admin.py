from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile, UserSubscription


@admin.register(UserProfile)
class CustomUserAdmin(UserAdmin):
    """Модернизация админки для модели пользователя."""

    list_display = ('id', 'email', 'username', 'first_name', 'last_name', 'is_active')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('id',)


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    """Админка для подписок пользователей."""

    list_display = ('subscriber', 'author')
    search_fields = ('subscriber__email', 'author__email')
    list_filter = ('subscriber',)
