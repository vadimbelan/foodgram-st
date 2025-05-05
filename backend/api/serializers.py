from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    Ingredient,
    Dish,
    IngredientAmount,
    FavoriteRecipe,
    ShoppingCartRecipe,
    UserSubscription,
)

User = get_user_model()


# ----------------------------------------------------- BASIC SERIALIZERS
class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class IngredientAmountSerializer(serializers.ModelSerializer):
    """
    Связка «продукт — кол‑во».

    Принимаем с клиента поле **amount**, а сохраняем
    во внутреннее `quantity`, так что API остаётся совместимо.
    """
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source="ingredient",
    )
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit", read_only=True
    )
    amount = serializers.IntegerField(min_value=1, source="quantity")

    class Meta:
        model = IngredientAmount
        fields = ("id", "name", "measurement_unit", "amount")


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Компактное представление рецепта (только чтение)."""
    class Meta:
        model = Dish
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = fields


# ---------------------------------------------------------- USER‑SIDE
class PublicUserSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "avatar",
            "is_subscribed",
        )

    def get_is_subscribed(self, author: User) -> bool:
        request = self.context.get("request")
        return (
            request
            and request.user.is_authenticated
            and UserSubscription.objects.filter(
                subscriber=request.user, author=author
            ).exists()
        )


class SubscribedAuthorSerializer(PublicUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source="recipes.count", read_only=True
    )

    class Meta(PublicUserSerializer.Meta):
        fields = (
            *PublicUserSerializer.Meta.fields,
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, author: User):
        limit = int(
            self.context["request"].query_params.get("recipes_limit") or 10**10
        )
        return ShortRecipeSerializer(
            author.recipes.all()[:limit], many=True
        ).data


# ----------------------------------------------------------- MAIN DISH
class RecipeSerializer(serializers.ModelSerializer):
    author = PublicUserSerializer(source="creator", read_only=True)
    ingredients = IngredientAmountSerializer(
        source="recipe_ingredients", many=True
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Dish
        fields = (
            "id",
            "name",
            "text",
            "image",
            "author",
            "cooking_time",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
        )

    # ─────────────────── flags ────────────────────
    def _flag(self, model, dish: Dish) -> bool:
        request = self.context.get("request")
        return (
            request
            and request.user.is_authenticated
            and model.objects.filter(user=request.user, dish=dish).exists()
        )

    def get_is_favorited(self, dish: Dish) -> bool:
        return self._flag(FavoriteRecipe, dish)

    def get_is_in_shopping_cart(self, dish: Dish) -> bool:
        return self._flag(ShoppingCartRecipe, dish)

    # ─────────────────── CRUD ─────────────────────
    def _bulk_save_ingredients(self, dish: Dish, items):
        IngredientAmount.objects.bulk_create(
            IngredientAmount(
                dish=dish,
                ingredient=item["ingredient"],
                quantity=item["quantity"],
            )
            for item in items
        )

    def create(self, validated_data):
        ingredients = validated_data.pop("recipe_ingredients", [])
        dish = super().create(validated_data)
        self._bulk_save_ingredients(dish, ingredients)
        return dish

    def update(self, instance, validated_data):
        ingredients = validated_data.pop("recipe_ingredients", [])
        # сначала очищаем старые связи и добавляем новые
        instance.recipe_ingredients.all().delete()
        self._bulk_save_ingredients(instance, ingredients)
        # сохраняем сам рецепт самым последним действием
        return super().update(instance, validated_data)
