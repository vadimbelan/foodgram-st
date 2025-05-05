from django.db.models import F, Sum
from django.http import FileResponse
from django.utils import timezone
from django.contrib.auth import get_user_model

from djoser.views import UserViewSet as DjoserUserViewSet

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.reverse import reverse

from recipes.models import (
    Ingredient,
    IngredientAmount,
    Dish,
    FavoriteRecipe,
    ShoppingCartRecipe,
    UserSubscription,
)
from .pagination import CustomPagination
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    ShortRecipeSerializer,
    SubscribedAuthorSerializer,
    PublicUserSerializer,
)

User = get_user_model()


# ───────────────────────────  INGREDIENTS  ─────────────────────────
class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        prefix = self.request.query_params.get("name")
        return (
            self.queryset.filter(name__istartswith=prefix.lower())
            if prefix
            else self.queryset
        )


# ───────────────────────────────  RECIPES  ─────────────────────────
class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Dish.objects.prefetch_related("recipe_ingredients__ingredient")
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPagination

    # ~~~~~~~~~~~~~~~~~~~ helpers ~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def _toggle(request, dish: Dish, model):
        if request.method == "POST":
            _, created = model.objects.get_or_create(
                user=request.user, dish=dish
            )
            if not created:
                raise ValidationError({"detail": "Рецепт уже присутствует"})
            return Response(
                ShortRecipeSerializer(dish).data,
                status=status.HTTP_201_CREATED,
            )

        get_object_or_404(model, user=request.user, dish=dish).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ~~~~~~~~~~~~~~~~~~~ queryset ~~~~~~~~~~~~~~~~~~
    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params

        if author := p.get("author"):
            qs = qs.filter(creator_id=author)

        if p.get("is_favorited") == "1" and self.request.user.is_authenticated:
            qs = qs.filter(favorites__user=self.request.user)

        if (
            p.get("is_in_shopping_cart") == "1"
            and self.request.user.is_authenticated
        ):
            qs = qs.filter(shoppingcarts__user=self.request.user)

        return qs

    # ~~~~~~~~~~~~~~~~~~~ create/update ~~~~~~~~~~~~~
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    # ~~~~~~~~~~~~~~~~~~~ extra actions ~~~~~~~~~~~~~
    @action(detail=True, methods=["post", "delete"], url_path="favorite", permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        dish = get_object_or_404(Dish, pk=pk)
        return self._toggle(request, dish, FavoriteRecipe)

    @action(detail=True, methods=["post", "delete"], url_path="shopping_cart", permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        dish = get_object_or_404(Dish, pk=pk)
        return self._toggle(request, dish, ShoppingCartRecipe)

    @action(detail=True, methods=["get"], url_path="get-link")
    def get_link(self, request, pk=None):
        return Response(
            {"short-link": request.build_absolute_uri(
                reverse("recipe-short-link", args=[pk])
            )}
        )

    @action(detail=False, methods=["get"], url_path="download_shopping_cart", permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        totals = (
            IngredientAmount.objects.filter(dish__shoppingcarts__user=request.user)
            .values(
                name=F("ingredient__name"),
                unit=F("ingredient__measurement_unit"),
            )
            .annotate(total=Sum("quantity"))
            .order_by("name")
        )

        dish_titles = (
            Dish.objects.filter(shoppingcarts__user=request.user)
            .values_list("name", flat=True)
            .order_by("name")
        )

        report_text = "\n".join(
            [
                f"Список покупок на {timezone.localdate():%d.%m.%Y}:",
                "Продукты:",
                *[
                    f"{idx}. {row['name'].capitalize()} ({row['unit']}) — {row['total']}"
                    for idx, row in enumerate(totals, 1)
                ],
                "",
                "Рецепты, для которых нужны эти продукты:",
                *[f"{idx}. {title}" for idx, title in enumerate(dish_titles, 1)],
            ]
        )

        return FileResponse(
            report_text,
            content_type="text/plain",
            filename="shopping_cart.txt",
        )


# ────────────────────────────────  USERS  ──────────────────────────
class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = PublicUserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPagination

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated], url_path="me")
    def me(self, request):
        return super().me(request)

    @action(detail=False, methods=["put", "delete"], url_path="me/avatar", permission_classes=[IsAuthenticated])
    def avatar(self, request):
        user = request.user
        if request.method == "PUT":
            ser = self.get_serializer(user, data=request.data, partial=True)
            ser.is_valid(raise_exception=True)
            ser.save()
            return Response({"avatar": ser.data["avatar"]})
        user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post", "delete"], url_path="subscribe", permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, pk=id)

        if author == request.user and request.method == "POST":
            raise ValidationError({"detail": "Нельзя подписаться на себя"})

        if request.method == "POST":
            sub, created = UserSubscription.objects.get_or_create(
                subscriber=request.user, author=author
            )
            if not created:
                raise ValidationError(
                    {"detail": "Уже подписаны на этого автора"}
                )
            return Response(
                PublicUserSerializer(author, context={"request": request}).data,
                status=status.HTTP_201_CREATED,
            )

        get_object_or_404(
            UserSubscription, subscriber=request.user, author=author
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], url_path="subscriptions", permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        qs = request.user.subscriptions.select_related("author")
        paginator = CustomPagination()
        page = paginator.paginate_queryset(qs, request)
        authors = [sub.author for sub in page]
        ser = SubscribedAuthorSerializer(
            authors, many=True, context={"request": request}
        )
        return paginator.get_paginated_response(ser.data)
