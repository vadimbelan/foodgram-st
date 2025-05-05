from django.contrib import admin

from .models import (
    Ingredient,
    Dish,
    IngredientAmount,
    FavoriteRecipe,
    ShoppingCartRecipe,
)


# ---------------------------------------------------- INGREDIENTS
@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    list_filter = ("measurement_unit",)
    search_fields = ("name",)
    ordering = ("name",)


# -------------------------------------------------------- DISHES
@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "creator", "fav_cnt")
    search_fields = ("title", "creator__username", "creator__email")
    list_filter = ("creator", "created_at")
    ordering = ("id",)

    @admin.display(description="В избранном")
    def fav_cnt(self, obj):
        return obj.favorites.count()


# -------------------------------------------- INGREDIENT AMOUNTS
@admin.register(IngredientAmount)
class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = ("dish", "ingredient", "amount")
    search_fields = ("dish__title", "ingredient__name")


# --------------------------------------- FAVS & SHOPPING CARTS
@admin.register(FavoriteRecipe, ShoppingCartRecipe)
class RelationAdmin(admin.ModelAdmin):
    list_display = ("user", "dish")
    list_filter = ("user",)
    search_fields = ("user__email", "dish__title")
