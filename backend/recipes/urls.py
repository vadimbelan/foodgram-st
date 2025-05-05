from django.urls import path

from .views import recipe_short_link

urlpatterns = [
    path("s/<int:pk>/", recipe_short_link, name="recipe-short-link"),
]
