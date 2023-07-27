from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Ingredient, Recipe,
                            AmountOfIngredient, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from api.utils import add_or_delete
from users.models import Subscription, User
from api.filters import IngredientFilter, RecipeFilter
from api.pagination import CustomPagination
from api.permissions import IsOwnerOrReadOnly
from api.serializers import (IngredientSerializer, FavoriteSerializer,
                             RecipeCreateSerializer, RecipeReadSerializer,
                             ShoppingCartSerializer,
                             SubscribeSerializer,
                             TagSerializer, UserSerializer)


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination
    permission_classes = [AllowAny]
    add_serializer = SubscribeSerializer

    @action(methods=['GET'], detail=False,
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = self.request.user
        authors = User.objects.filter(followings__user=user)
        page = self.paginate_queryset(authors)
        serializer = SubscribeSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        user = self.request.user
        author = get_object_or_404(User, id=id)
        subscription = Subscription.objects.filter(user=user, author=author)

        if request.method == 'POST':
            if subscription.exists():
                return Response(
                    {'error': 'Вы уже подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = SubscribeSerializer(
                author,
                context={'request': request}
            )
            Subscription.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not subscription.exists():
                return Response(
                    {'error': 'Вы не подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,]
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter
    pagination_class = None


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,]
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsOwnerOrReadOnly, )
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=[IsAuthenticated])
    def favorite(self, request, id):
        return add_or_delete(id, FavoriteSerializer)

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, id):
        return add_or_delete(id, ShoppingCartSerializer)

    @action(methods=['GET'], detail=False,
            permission_classes=[IsAuthenticated], pagination_class=None)
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(
                'Корзина пустая', status=status.HTTP_400_BAD_REQUEST)

        ingredients = AmountOfIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        filename = f'{user.username}_shopping_list.txt'
        shopping_list = ['Список покупок:\n']
        for ing in ingredients:
            shopping_list += (
                f'{ing["ingredients"]} - {ing["amount"]}, {ing["measure"]}\n'
            )
        response = HttpResponse(shopping_list,
                                content_type='text.txt; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
