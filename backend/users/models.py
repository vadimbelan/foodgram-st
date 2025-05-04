from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class UserProfile(AbstractUser):
    """Пользовательская модель с расширенными полями."""

    email = models.EmailField(unique=True, max_length=254)
    username = models.CharField(
        max_length=150, unique=True, validators=[RegexValidator(
            regex=r'^[\w.@+-]+$', message='Допустимы только буквы, цифры и символы: @ . + -'
        )]
    )
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('email',)

    def __str__(self):
        return self.email


User = get_user_model()


class UserSubscription(models.Model):
    """Модель подписки пользователя на авторов рецептов."""

    subscriber = models.ForeignKey(
        User, related_name="subscriptions", on_delete=models.CASCADE, verbose_name="Подписчик"
    )
    author = models.ForeignKey(
        User, related_name="subscribed_by", on_delete=models.CASCADE, verbose_name="Автор"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["subscriber", "author"], name="unique_subscription")
        ]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return f"{self.subscriber} подписан на {self.author}"
