from django.shortcuts import HttpResponse, get_object_or_404
from djoser.views import UserViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets, filters
from rest_framework.decorators import action, permission_classes as permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientSearchFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly, IsAdminOrReadOnly
from .serializers import (CustomUserSerialaizer, FavoriteSerializer,
                          IngredientSerializer, RecipeCreateSerialaizer,
                          RecipeReadSerialaizer, ShopingCartSerializer,
                          SubscribeSerializer, SubscriptionsSerializer,
                          TagSerializer)
from recipes.models import (Favorite, Ingredient, Recipe, RecipesIngredients,
                            ShopingCart, Tag)
from users.models import Subscribe, User


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = RecipeFilter
    ordering_fields = ('pub_date',)
    ordering = ('-pub_date',)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerialaizer
        return RecipeCreateSerialaizer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=('post', 'delete'), detail=True)
    @permissions([IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        user_id = request.user.id
        serializer = FavoriteSerializer(
            data={'user': request.user.id, 'recipe': recipe.id}
        )
        obj_exists = Favorite.objects.filter(
            recipe=pk, user=user_id
        ).exists()
        if request.method == "POST":
            if obj_exists:
                return Response(
                    'Рецепт уже добавлен в избранное',
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.is_valid(raise_exception=True)
            serializer.save(recipe=recipe, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not obj_exists:
            return Response(
                'Рецепт отсутствует в избранном',
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite = get_object_or_404(
            Favorite, user=request.user, recipe__id=pk
        )
        favorite.delete()
        return Response(
            f'Рецепт {favorite.recipe} удален из избранного у пользователя'
            f' {request.user}', status=status.HTTP_204_NO_CONTENT
        )

    @action(methods=('post', 'delete'), detail=True)
    @permissions([IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        user_id = request.user.id
        serializer = ShopingCartSerializer(
            data={'user': user_id, 'recipe': recipe.id}
        )
        obj_exists = ShopingCart.objects.filter(
            recipe=pk, user=user_id
        ).exists()
        if request.method == "POST":
            if obj_exists:
                return Response(
                    'Рецепт уже добавлен в список покупок',
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.is_valid(raise_exception=True)
            serializer.save(recipe=recipe, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not obj_exists:
            return Response(
                'Рецепт отсутствует в списке покупок',
                status=status.HTTP_400_BAD_REQUEST
            )
        shoping_cart = get_object_or_404(
            ShopingCart, user=request.user, recipe__id=pk
        )
        shoping_cart.delete()
        return Response(
            f'Рецепт {shoping_cart.recipe} удален из списка покупок '
            f'пользователя {request.user}', status=status.HTTP_204_NO_CONTENT
        )

    @action(methods=('get',), detail=False)
    @permissions([IsAuthenticated])
    def download_shopping_cart(self, request):
        shoping_cart = {}
        ingredients = RecipesIngredients.objects.filter(
            recipe__shopingcart__user=request.user
        )
        for ingredient in ingredients:
            amount = ingredient.amount
            name = ingredient.ingredient.name
            measurement_unit = ingredient.ingredient.measurement_unit
            if name not in shoping_cart:
                shoping_cart[name] = {
                    'measurement_unit': measurement_unit,
                    'amount': amount
                }
            else:
                shoping_cart[name]['amount'] += amount
        shopping_list = (
            [f"- {item}: {value['amount']}"
             f" {value['measurement_unit']}\n"
             for item, value in shoping_cart.items()]
        )
        response = HttpResponse(shopping_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = ('attachment; filename='
                                           '"shopping_list.txt"')
        return response


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerialaizer

    @action(methods=('get',), detail=False)
    @permissions([IsAuthenticated])
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(
            queryset,
            many=True,
            context={'request': self.request}
        )
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(methods=('post', 'delete'), detail=True)
    @permissions([IsAuthenticated])
    def subscribe(self, request, id=None):
        author = self.get_object()
        user = request.user
        serializer = SubscribeSerializer(data={'user': user.id, 'author': id})
        if request.method == "POST":
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user)
            serializer = SubscriptionsSerializer(
                author, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        subscribe = get_object_or_404(Subscribe, user=user, author__id=id)
        subscribe.delete()
        return Response(
            f'Пользователь {user} отписался от {subscribe.author}',
            status=status.HTTP_204_NO_CONTENT
        )


class TagsViewSet(viewsets.ModelViewSet):
    pagination_class = None
    queryset = Tag.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = TagSerializer
    search_fields = ('name',)


class IngredientsViewSet(viewsets.ModelViewSet):
    pagination_class = None
    queryset = Ingredient.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_class = IngredientSearchFilter
