from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from .models import Dish


def recipe_short_link(request, pk: int):
    """
    /s/<pk>/  → постоянный редирект на полный DRF‑эндпоинт рецепта.
    """
    get_object_or_404(Dish, pk=pk)  # 404, если нет рецепта
    url = reverse("recipes-detail", kwargs={"pk": pk})
    return redirect(url, permanent=True)
