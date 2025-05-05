from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipeViewSet, UserViewSet

# собираем все viewset’ы в единый роутер
router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")
router.register(r"ingredients", IngredientViewSet, basename="ingredients")
router.register(r"recipes", RecipeViewSet, basename="recipes")

urlpatterns = [
    # основной набор эндпоинтов из роутера
    path("", include(router.urls)),
    # токены аутентификации через djoser
    path("auth/", include("djoser.urls.authtoken")),
    # короткая ссылка на рецепт
    path(
        "s/<int:pk>/",
        RecipeViewSet.as_view({"get": "get_short_link"}),
        name="recipe-short-link",
    ),
]
