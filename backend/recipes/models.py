from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


# ─────────────────────────────  USER  ──────────────────────────────
class UserProfile(AbstractUser):
    """Пользователь (аутентификация по email)."""
    email = models.EmailField(_("email address"), unique=True, max_length=254)
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[\w.@+-]+$",
                message=_("Допустимы только буквы, цифры и символы @ . + - _"),
            )
        ],
    )
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    avatar = models.ImageField(
        _("avatar"),
        upload_to="avatars/",
        blank=True,
        null=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name", "password"]

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")
        ordering = ("email",)

    def __str__(self):
        return self.email


# alias для get_user_model()
User = UserProfile


class UserSubscription(models.Model):
    """Подписка «читатель → автор»."""
    subscriber = models.ForeignKey(
        User,
        related_name="subscriptions",
        on_delete=models.CASCADE,
        verbose_name=_("Подписчик"),
    )
    author = models.ForeignKey(
        User,
        related_name="followers",
        on_delete=models.CASCADE,
        verbose_name=_("Автор"),
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("subscriber", "author"),
                name="unique_subscription",
            )
        ]
        verbose_name = _("Подписка")
        verbose_name_plural = _("Подписки")

    def __str__(self):
        return f"{self.subscriber} → {self.author}"


# ────────────────────────────  INGREDIENT  ─────────────────────────
class Ingredient(models.Model):
    """Продукт из справочника."""
    name = models.CharField(_("Название"), max_length=128)
    measurement_unit = models.CharField(_("Ед. изм."), max_length=64)

    class Meta:
        ordering = ("name",)
        verbose_name = _("Продукт")
        verbose_name_plural = _("Продукты")
        constraints = [
            models.UniqueConstraint(
                fields=("name", "measurement_unit"),
                name="unique_ingredient_name_unit",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"


# ───────────────────────────────  DISH  ────────────────────────────
class Dish(models.Model):
    """Рецепт (блюдо)."""
    name = models.CharField(_("Название рецепта"), max_length=256)
    text = models.TextField(_("Описание"))
    image = models.ImageField(_("Фото"), upload_to="dishes/images/")
    creator = models.ForeignKey(
        User,
        related_name="recipes",
        on_delete=models.CASCADE,
        verbose_name=_("Автор"),
    )
    cooking_time = models.PositiveIntegerField(
        _("Время готовки, мин"), validators=[MinValueValidator(1)]
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientAmount",
        related_name="dishes",
        verbose_name=_("Продукты"),
    )
    created_at = models.DateTimeField(_("Дата публикации"), auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Рецепт")
        verbose_name_plural = _("Рецепты")

    def __str__(self):
        return f"{self.name} (id={self.id})"


# ─────────────  LINK  Dish ↔ Ingredient (с кол‑вом)  ──────────────
class IngredientAmount(models.Model):
    dish = models.ForeignKey(
        Dish,
        related_name="recipe_ingredients",
        on_delete=models.CASCADE,
        verbose_name=_("Рецепт"),
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name="ingredient_usages",
        on_delete=models.CASCADE,
        verbose_name=_("Продукт"),
    )
    quantity = models.PositiveIntegerField(
        _("Количество"), validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = _("Продукт рецепта")
        verbose_name_plural = _("Продукты рецептов")
        constraints = [
            models.UniqueConstraint(
                fields=("dish", "ingredient"),
                name="unique_dish_ingredient",
            )
        ]

    def __str__(self):
        return (
            f"{self.ingredient.name} — {self.quantity} "
            f"{self.ingredient.measurement_unit} для «{self.dish.name}»"
        )


# ────────────────────────  USER–DISH relations  ───────────────────
class BaseUserDishRelation(models.Model):
    """Абстрактная связь «пользователь — рецепт»."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_("Пользователь")
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=("user", "dish"), name="%(class)s_user_dish_unique"
            )
        ]

    def __str__(self):
        return f"{self.user} → {self.dish}"


class FavoriteRecipe(BaseUserDishRelation):
    dish = models.ForeignKey(
        Dish,
        related_name="favorites",      # ← нужное имя для админки и API
        on_delete=models.CASCADE,
        verbose_name=_("Рецепт"),
    )

    class Meta(BaseUserDishRelation.Meta):
        verbose_name = _("Избранный рецепт")
        verbose_name_plural = _("Избранные рецепты")


class ShoppingCartRecipe(BaseUserDishRelation):
    dish = models.ForeignKey(
        Dish,
        related_name="shoppingcarts",  # ← нужно для флага is_in_shopping_cart
        on_delete=models.CASCADE,
        verbose_name=_("Рецепт"),
    )

    class Meta(BaseUserDishRelation.Meta):
        verbose_name = _("Корзина покупок")
        verbose_name_plural = _("Корзины покупок")
