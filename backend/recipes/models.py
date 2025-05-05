from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.contrib.auth import get_user_model


# ─────────────────────────────  USER  ──────────────────────────────
class UserProfile(AbstractUser):
    """Пользователь (аутентификация по email)."""
    email = models.EmailField("E‑mail", unique=True, max_length=254)
    username = models.CharField(
        "Имя пользователя",
        max_length=150,
        unique=True,
        validators=[RegexValidator(regex=r"^[\w.@+-]+$")],
    )
    first_name = models.CharField("Имя", max_length=150, blank=True)
    last_name = models.CharField("Фамилия", max_length=150, blank=True)
    avatar = models.ImageField(
        "Аватар",
        upload_to="avatars/",
        blank=True,
        null=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name", "password"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("email",)

    def __str__(self):
        return self.email


# alias для get_user_model()
User = get_user_model()


class UserSubscription(models.Model):
    """Подписка «читатель → автор»."""
    subscriber = models.ForeignKey(
        User,
        related_name="subscriptions",
        on_delete=models.CASCADE,
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        related_name="authors",      # авторы, на которых подписан пользователь
        on_delete=models.CASCADE,
        verbose_name="Автор",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("subscriber", "author"),
                name="unique_subscription",
            )
        ]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return f"{self.subscriber} → {self.author}"


# ────────────────────────────  INGREDIENT  ─────────────────────────
class Ingredient(models.Model):
    """Продукт из справочника."""
    name = models.CharField("Название", max_length=128)
    measurement_unit = models.CharField("Ед. изм.", max_length=64)

    class Meta:
        ordering = ("name",)
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
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
    name = models.CharField("Название рецепта", max_length=256)
    text = models.TextField("Описание")
    image = models.ImageField("Фото", upload_to="dishes/images/")
    creator = models.ForeignKey(
        User,
        related_name="recipes",
        on_delete=models.CASCADE,
        verbose_name="Автор",
    )
    cooking_time = models.PositiveIntegerField(
        "Время готовки, мин", validators=[MinValueValidator(1)]
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientAmount",
        related_name="dishes",
        verbose_name="Продукты",
    )
    created_at = models.DateTimeField("Дата публикации", auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return f"{self.name} (id={self.id})"


# ─────────────  LINK  Dish ↔ Ingredient (с кол‑вом)  ──────────────
class IngredientAmount(models.Model):
    dish = models.ForeignKey(
        Dish,
        related_name="recipe_ingredients",
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name="ingredient_usages",
        on_delete=models.CASCADE,
        verbose_name="Продукт",
    )
    quantity = models.PositiveIntegerField(
        "Мера", validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = "Продукт рецепта"
        verbose_name_plural = "Продукты рецептов"
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
        User,
        related_name="%(class)s_relations",  # уникально для каждого наследника
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
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
        related_name="favorites",
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )

    class Meta(BaseUserDishRelation.Meta):
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"


class ShoppingCartRecipe(BaseUserDishRelation):
    dish = models.ForeignKey(
        Dish,
        related_name="shoppingcarts",
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )

    class Meta(BaseUserDishRelation.Meta):
        verbose_name = "Корзина покупок"
        verbose_name_plural = "Корзины покупок"
