from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from django.core.validators import MinValueValidator

from recipes.models import Dish, Ingredient, IngredientAmount
from users.models import Subscription, User


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиента."""

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиента в рецепте."""

    id = serializers.PrimaryKeyRelatedField(source="ingredient", queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(source="ingredient.measurement_unit")
    quantity = serializers.IntegerField(min_value=1, validators=[MinValueValidator(1)])

    class Meta:
        model = IngredientAmount
        fields = ("id", "name", "measurement_unit", "quantity")


class DishSerializer(serializers.ModelSerializer):
    """Сериализатор для рецепта."""

    creator = serializers.StringRelatedField(read_only=True)
    ingredients = IngredientAmountSerializer(source="ingredientamount_set", many=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Dish
        fields = ("id", "title", "description", "image", "creator", "cook_time", "ingredients", "is_favorited", "is_in_shopping_cart")

    def get_is_favorited(self, obj):
        """Проверка, добавлен ли рецепт в избранное."""
        user = self.context["request"].user
        return user.is_authenticated and obj.favorites.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверка, есть ли рецепт в корзине покупок."""
        user = self.context["request"].user
        return user.is_authenticated and obj.shoppingcarts.filter(user=user).exists()


class ShortDishSerializer(serializers.ModelSerializer):
    """Укороченный сериализатор для отображения рецептов в подписках."""

    class Meta:
        model = Dish
        fields = ("id", "title", "image", "cook_time")
