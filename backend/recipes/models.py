from django.core.validators import MinValueValidator
from django.db import models
from users.models import User

# ----------------------------------------------------- BASE DATA
class Ingredient(models.Model):
    """Справочник ингредиентов."""
    name = models.CharField(max_length=128, verbose_name="Название")
    measurement_unit = models.CharField(max_length=64, verbose_name="Ед. изм.")

    class Meta:
        ordering = ("name",)
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        constraints = [
            models.UniqueConstraint(
                fields=("name", "measurement_unit"),
                name="unique_ingredient_name_unit",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"

# ------------------------------------------------------- RECIPE
class Dish(models.Model):
    """Рецепт (блюдо)."""
    title = models.CharField(max_length=256, verbose_name="Название рецепта")
    description = models.TextField(verbose_name="Описание")
    image = models.ImageField(upload_to="dishes/images/", verbose_name="Фото")
    creator = models.ForeignKey(
        User,
        related_name="recipes",
        on_delete=models.CASCADE,
        verbose_name="Автор",
    )
    cook_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1, "Минимум 1 минута")],
        verbose_name="Время приготовления, мин",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientAmount",
        related_name="dishes",
        verbose_name="Ингредиенты",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации",
    )

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return f"{self.title} (id={self.id})"

# --------------------------------------- LINK RECIPE <-> INGREDIENT
class IngredientAmount(models.Model):
    """Количество ингредиента в рецепте."""
    dish = models.ForeignKey(
        Dish,
        related_name="recipe_ingredients",
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name="ingredient_recipes",
        on_delete=models.CASCADE,
        verbose_name="Ингредиент",
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1, "Минимум 1")],
        verbose_name="Количество",
    )

    class Meta:
        verbose_name = "Ингредиент рецепта"
        verbose_name_plural = "Ингредиенты рецептов"
        constraints = [
            models.UniqueConstraint(
                fields=("dish", "ingredient"),
                name="unique_dish_ingredient",
            )
        ]

    def __str__(self):
        return (
            f"{self.ingredient.name} — {self.amount} "
            f"{self.ingredient.measurement_unit} для «{self.dish.title}»"
        )

# ---------------------------------------------------- RELATIONS
class FavoriteRecipe(models.Model):
    """Избранные рецепты пользователя."""
    user = models.ForeignKey(
        User,
        related_name="favorite_recipes",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    dish = models.ForeignKey(
        Dish,
        related_name="favorites",
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        constraints = [
            models.UniqueConstraint(
                fields=("user", "dish"),
                name="unique_favorite_user_dish",
            )
        ]

    def __str__(self):
        return f"{self.user} → {self.dish}"


class ShoppingCartRecipe(models.Model):
    """Рецепты в корзине пользователя."""
    user = models.ForeignKey(
        User,
        related_name="shopping_cart_recipes",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    dish = models.ForeignKey(
        Dish,
        related_name="shoppingcarts",
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Корзина покупок"
        verbose_name_plural = "Корзины покупок"
        constraints = [
            models.UniqueConstraint(
                fields=("user", "dish"),
                name="unique_cart_user_dish",
            )
        ]

    def __str__(self):
        return f"{self.user} → {self.dish}"
