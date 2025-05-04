from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from users.models import UserProfile, UserSubscription
from api.serializers import ShortRecipeSerializer


class UserProfileSerializer(DjoserUserSerializer):
    avatar = Base64ImageField(required=False)
    is_subscribed = serializers.SerializerMethodField()

    class Meta(DjoserUserSerializer.Meta):
        model = UserProfile
        fields = (*DjoserUserSerializer.Meta.fields, "avatar", "is_subscribed")

    def get_is_subscribed(self, obj):
        req = self.context.get("request")
        return (
            req
            and req.user.is_authenticated
            and UserSubscription.objects.filter(
                subscriber=req.user, author=obj
            ).exists()
        )


class ShortUserSerializer(UserProfileSerializer):
    recipes_count = serializers.IntegerField(
        source="recipes.count", read_only=True
    )

    class Meta(UserProfileSerializer.Meta):
        fields = (*UserProfileSerializer.Meta.fields, "recipes_count")


class UserSubscriptionSerializer(ShortUserSerializer):
    recipes = serializers.SerializerMethodField()

    class Meta(ShortUserSerializer.Meta):
        fields = (*ShortUserSerializer.Meta.fields, "recipes")

    def get_recipes(self, author):
        limit = int(
            self.context["request"].query_params.get("recipes_limit", 10**10)
        )
        qs = author.recipes.all()[:limit]
        return ShortRecipeSerializer(qs, many=True).data
