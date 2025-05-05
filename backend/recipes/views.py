from django.http import Http404
from django.shortcuts import redirect
from recipes.models import Dish


def recipe_short_link(request, pk: int):
    """
    /s/<pk>/ → постоянный редирект на полный DRF‑эндпоинт рецепта.
    """
    if not Dish.objects.filter(pk=pk).exists():
        raise Http404("Рецепт не найден")

    return redirect(f"/api/recipes/{pk}/", permanent=True)
