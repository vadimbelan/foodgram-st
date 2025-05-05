from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import models
from django.utils.safestring import mark_safe

from .models import (
    UserProfile,
    UserSubscription,
    Ingredient,
    Dish,
    IngredientAmount,
    FavoriteRecipe,
    ShoppingCartRecipe,
)


# ────────────────────────────  USERS  ─────────────────────────────
@admin.register(UserProfile)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "id",
        "email",
        "username",
        "first_name",
        "last_name",
        "is_active",
        "recipes_count",
        "subscribers_count",
    )
    readonly_fields = ("recipes_count", "subscribers_count", "avatar_preview")
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("avatar", "avatar_preview")}),
    )
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("id",)

    @admin.display(description="Рецептов")
    def recipes_count(self, user: UserProfile):
        return user.recipes.count()

    @admin.display(description="Подписчиков")
    def subscribers_count(self, user: UserProfile):
        return user.followers.count()

    @admin.display(description="Превью")
    def avatar_preview(self, user: UserProfile):
        if user.avatar:
            return mark_safe(f'<img src="{user.avatar.url}" height="64" />')
        return "—"


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "subscriber", "author")
    list_filter = ("subscriber", "author")
    search_fields = ("subscriber__email", "author__email")
    ordering = ("id",)


# ──────────────────────────  INGREDIENTS  ─────────────────────────
class IngredientUsedFilter(admin.SimpleListFilter):
    """Есть ли продукт хотя бы в одном рецепте."""
    title = "Использование"
    parameter_name = "used"

    def lookups(self, request, model_admin):
        return (("yes", "Есть в рецептах"), ("no", "Не используется"))

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(dishes__isnull=False).distinct()
        if self.value() == "no":
            return queryset.filter(dishes__isnull=True)
        return queryset


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "measurement_unit", "recipes_total")
    list_filter = ("measurement_unit", IngredientUsedFilter)
    search_fields = ("name", "measurement_unit")

    @admin.display(description="В рецептах")
    def recipes_total(self, ingredient: Ingredient):
        return ingredient.dishes.count()


# кастом‑фильтр времени готовки (быстро / средне / долго)
class CookingTimeFilter(admin.SimpleListFilter):
    title = "Время готовки"
    parameter_name = "cooking_category"

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        agg = qs.aggregate(
            min_time=models.Min("cooking_time"), max_time=models.Max("cooking_time")
        )
        low = agg["min_time"] or 0
        high = agg["max_time"] or 60
        mid = (low + high) // 2
        return (
            ("fast", f"≤ {mid // 2} мин"),
            ("medium", f"{mid // 2 + 1}‑{mid} мин"),
            ("slow", f"> {mid} мин"),
        )

    def queryset(self, request, queryset):
        val = self.value()
        if not val:
            return queryset
        agg = queryset.aggregate(
            min_time=models.Min("cooking_time"), max_time=models.Max("cooking_time")
        )
        low = agg["min_time"] or 0
        high = agg["max_time"] or 60
        mid = (low + high) // 2
        if val == "fast":
            return queryset.filter(cooking_time__lte=mid // 2)
        if val == "medium":
            return queryset.filter(cooking_time__gt=mid // 2, cooking_time__lte=mid)
        return queryset.filter(cooking_time__gt=mid)


# ────────────────────────────  DISHES  ────────────────────────────
@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "cooking_time",
        "creator",
        "favorites_total",
        "ingredients_list",
        "image_preview",
    )
    list_filter = ("creator", "created_at", CookingTimeFilter)
    search_fields = ("name", "creator__username", "creator__email")
    ordering = ("-created_at",)
    readonly_fields = ("image_preview", "ingredients_list")

    @admin.display(description="В избранном")
    def favorites_total(self, dish: Dish):
        return dish.favorites.count()

    @admin.display(description="Продукты")
    def ingredients_list(self, dish: Dish):
        items = (
            dish.recipe_ingredients.select_related("ingredient")
            .values_list(
                "ingredient__name", "quantity", "ingredient__measurement_unit"
            )
        )
        html = "<br>".join(
            f"{name} — {qty} {unit}" for name, qty, unit in items
        )
        return mark_safe(html) if html else "—"

    @admin.display(description="Фото")
    def image_preview(self, dish: Dish):
        if dish.image:
            return mark_safe(f'<img src="{dish.image.url}" height="80" />')
        return "—"


@admin.register(IngredientAmount)
class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = ("id", "dish", "ingredient", "quantity")
    list_filter = ("ingredient",)
    search_fields = ("dish__name", "ingredient__name")


@admin.register(FavoriteRecipe, ShoppingCartRecipe)
class RelationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "dish")
    list_filter = ("user",)
    search_fields = ("user__email", "dish__name")
    ordering = ("id",)
