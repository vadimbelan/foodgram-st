from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from users.models import UserProfile, UserSubscription
from users.serializers import UserProfileSerializer, UserSubscriptionSerializer, ShortUserSerializer
from recipes.models import Dish


class UserProfileViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с профилем пользователя."""

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None

    # Получение информации о текущем пользователе
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Получение данных о текущем пользователе."""
        return Response(self.get_serializer(request.user).data)

    # Смена аватара
    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar')
    def change_avatar(self, request):
        """Метод для изменения или удаления аватара."""
        user = request.user
        if request.method == 'PUT':
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'avatar': serializer.data['avatar']}, status=status.HTTP_200_OK)
        
        # DELETE
        user.avatar.delete()
        return Response({'message': 'Аватар удалён'}, status=status.HTTP_204_NO_CONTENT)

    # Подписка и отписка
    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def subscribe_and_unsubscribe(self, request, id=None):
        """Подписка на пользователя (или отписка)."""
        author = get_object_or_404(UserProfile, pk=id)
        if author == request.user:
            raise ValidationError({'error': 'Нельзя подписаться на самого себя'})

        if request.method == 'POST':
            subscription, created = UserSubscription.objects.get_or_create(subscriber=request.user, author=author)
            if not created:
                raise ValidationError({'error': 'Подписка уже оформлена'})
            return Response({'user': subscription.subscriber.username, 'author': subscription.author.username},
                            status=status.HTTP_201_CREATED)

        # DELETE
        get_object_or_404(UserSubscription, subscriber=request.user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # Список подписок пользователя
    @action(detail=False, methods=['get'], url_path='subscriptions')
    def subscriptions(self, request):
        """Получить список авторов, на которых подписан пользователь."""
        user = request.user
        subscriptions = user.subscriptions.select_related('author')
        serializer = UserSubscriptionSerializer(subscriptions, many=True, context={'request': request})
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с пользователями."""

    queryset = UserProfile.objects.all()
    serializer_class = ShortUserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    # Получение краткой информации о пользователе
    @action(detail=False, methods=['get'], url_path='me')
    def get_me(self, request):
        """Получить текущего пользователя."""
        return Response(self.get_serializer(request.user).data)
