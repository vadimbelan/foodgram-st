from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import models
from django.utils.html import format_html

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
class UserProfileAdmin(UserAdmin):
    list_display = (
        "id",
        "email",
        "username",
        "first_name",
        "last_name",
        "is_active",
        "recipes_count",
        "subscribers_count",
        "subscriptions_count",
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

    @admin.display(description="Подписок")
    def subscriptions_count(self, user: UserProfile):
        return user.subscriptions.count()

    @admin.display(description="Превью")
    def avatar_preview(self, user: UserProfile):
        if user.avatar:
            return format_html('<img src="{}" height="64" />', user.avatar.url)
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
    LOOKUPS = (("yes", "Есть в рецептах"), ("no", "Не используется"))

    def lookups(self, request, model_admin):
        return self.LOOKUPS

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
            min_time=models.Min("cooking_time"),
            max_time=models.Max("cooking_time"),
        )
        self.low = agg["min_time"] or 0
        self.high = agg["max_time"] or 60
        self.mid = (self.low + self.high) // 2
        return (
            ("fast", f"≤ {self.mid} мин"),
            ("medium", f"{self.mid + 1}‑{self.high} мин"),
            ("slow", f"> {self.high} мин"),
        )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        if self.value() == "fast":
            return queryset.filter(cooking_time__lte=self.mid)
        if self.value() == "medium":
            return queryset.filter(
                cooking_time__gt=self.mid, cooking_time__lte=self.high
            )
        return queryset.filter(cooking_time__gt=self.high)


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
        return format_html(
            "<br>".join(
                f"{item.ingredient.name} — {item.quantity} "
                f"{item.ingredient.measurement_unit}"
                for item in dish.recipe_ingredients.select_related("ingredient")
            ) or "—"
        )

    @admin.display(description="Фото")
    def image_preview(self, dish: Dish):
        if dish.image:
            return format_html('<img src="{}" height="80" />', dish.image.url)
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
