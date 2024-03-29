from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.decorators import permission_classes as permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Subscribe, User

from .filters import IngredientSearchFilter, RecipeFilter
from .paginators import CustomPageNumberPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (CustomUserSerialaizer, FavoriteSerializer,
                          IngredientSerializer, RecipeCreateSerialaizer,
                          RecipeReadSerialaizer, ShoppingCartSerializer,
                          SubscribeSerializer, SubscriptionsSerializer,
                          TagSerializer)
from .utils import (FAVORITE_EXISTS_MESSAGE, FAVORITE_MISSING_MESSAGE,
                    FROM_FAVORITE, FROM_SHOPING_CART,
                    SHOPING_CART_EXISTS_MESSAGE, SHOPING_CART_MISSING_MESSAGE,
                    UNSUBSCRIBE_MESSAGE, create_delete_object)


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с рецептами."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = RecipeFilter
    ordering_fields = ('pub_date',)
    ordering = ('-pub_date',)

    def get_serializer_class(self):
        """Возвращает класс сериализатора.

        Returns:
            Если метод запроса "GET":
                RecipeReadSerialaizer: класс сериализатора для вывода списка
                рецептов.
            Иначе:
                RecipeCreateSerialaizer: класс сериализатора для создания
                рецепта.
        """
        if self.request.method == 'GET':
            return RecipeReadSerialaizer
        return RecipeCreateSerialaizer

    def perform_create(self, serializer):
        """Сохраняет текущего пользователя в качестве автора при создании
        рецепта.

        Args:
            serializer (RecipeCreateSerialaizer): объект сериализатора для
            создания рецепта.
        """
        serializer.save(author=self.request.user)

    @action(methods=('post', 'delete'), detail=True)
    @permissions([IsAuthenticated])
    def favorite(self, request, pk=None):
        """Добавляет/удаляет рецепт из избранного.

        Args:
            request (Request): объект запроса.
            pk (int, опционально): id рецепта. По умолчанию None.

        Returns:
            Если метод запроса "POST":
                Response: сериализованные данные если такого рецепта нету в
                избранном иначе сообщение о том что такой рецепта уже
                присутствует.
            Иначе:
                Response: сообщение о том что рецепт удален из избранного иначе
                сообщение о том что такого рецепта нету в избранном.
        """

        return create_delete_object(
            request,
            pk,
            FavoriteSerializer,
            Favorite,
            FAVORITE_EXISTS_MESSAGE,
            FAVORITE_MISSING_MESSAGE,
            FROM_FAVORITE
        )

    @action(methods=('post', 'delete'), detail=True)
    @permissions([IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        """Добавляет/удаляет рецепт из списка покупок.

        Args:
            request (Request): объект запроса.
            pk (int, опционально): id рецепта. По умолчанию None.

        Returns:
            Если метод запроса "POST":
                Response: сериализованные данные если такого рецепта нету в
                списке покупок иначе сообщение о том что такой рецепт уже
                присутствует.
            Иначе:
                Response: сообщение о том что рецепт удален из списка покупок
                иначе сообщение о том что такого рецепта нету в списке покупок.
        """

        return create_delete_object(
            request,
            pk,
            ShoppingCartSerializer,
            ShoppingCart,
            SHOPING_CART_EXISTS_MESSAGE,
            SHOPING_CART_MISSING_MESSAGE,
            FROM_SHOPING_CART
        )

    @action(methods=('get',), detail=False)
    @permissions([IsAuthenticated])
    def download_shopping_cart(self, request):
        """Скачивает текстовый файл с ингридиентами из списка покупок.

        Args:
            request (Request): объект запроса.

        Returns:
            HttpResponse: объект ответа.
        """
        shopping_cart = {}
        # Фильтруем объекты RecipeIngredient по текущему пользователю,
        # достаем поля ингредиента(только 'name' и 'measurement_unit')
        # и суммируем в поле ingredient_amount количество каждого ингредиента
        # затем создаем кортеж со значениями этих полей.
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount')).values_list(
            'ingredient__name',
            'ingredient__measurement_unit',
            'ingredient_amount'
        )
        for ingredient in ingredients:
            shopping_cart[ingredient[0]] = (ingredient[1], ingredient[2])
        shopping_list = '\n'.join(
            [f"- {item}: {value[1]} {value[0]}"
             for item, value in shopping_cart.items()]
        )
        response = HttpResponse(shopping_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = ('attachment; filename='
                                           '"shopping_list.txt"')
        return response


class CustomUserViewSet(UserViewSet):
    """ViewSet для работы с пользователями."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerialaizer

    @action(methods=('get',), detail=False)
    @permissions([IsAuthenticated])
    def subscriptions(self, request):
        """Выводит список подписок.

        Args:
            request (Request): объект запроса.

        Returns:
            Разбитый на страницы список подписок если их количество больше
            установленного в настройках пагинатора.
        """
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
        """Подписывает/отписывает пользователя от автора.

        Args:
            request (Request): объект запроса.
            id (int, optional): id автора. По умолчанию None.

        Returns:
            Если метод запроса "POST":
                Response: при успешной попытке подписки выводит имя
                пользователя и автора на которого он подписался.
            Иначе:
                Response: при успшной попытке отписки выводит сообщение о том
                что пользователь отписался от автора.
        """

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
            UNSUBSCRIBE_MESSAGE.format(user=user, author=subscribe.author),
            status=status.HTTP_204_NO_CONTENT
        )


class TagsViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с тегами."""

    pagination_class = None
    queryset = Tag.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = TagSerializer
    search_fields = ('name',)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для работы с ингредиентами."""

    pagination_class = None
    queryset = Ingredient.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_class = IngredientSearchFilter
