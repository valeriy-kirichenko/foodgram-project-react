from django_filters.rest_framework import FilterSet, filters
from recipes.models import Ingredient, Recipe, Tag


class IngredientSearchFilter(FilterSet):
    """Фильтрует ингредиенты при их поиске при создании рецепта.

    Для корректной работы поиска необходимо использовать кириллицу.
    Название ингредиента должно начинаться с набранных символов.
    """

    name = filters.CharFilter(field_name="name", lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', )


class RecipeFilter(FilterSet):
    """Фильтрует выдачу рецептов."""

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )
    is_favorited = filters.BooleanFilter(
        method='get_is_favorited',
        label="Есть подписка?"
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart',
        label="В списке покупок?"
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        """Возвращает список рецептов на авторов которых подписан пользователь.

        Args:
            queryset (QuerySet): Список обьектов.
            name : Не используется.
            value (bool): Значение из запроса.

        Returns:
            QuerySet: Список рецептов на авторов которых подписан пользователь.
        """
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        """Возвращает список рецептов находящихся в списке покупок
        пользователя.

        Args:
            queryset (QuerySet): Список обьектов.
            name : Не используется.
            value (bool): Значение из запроса.

        Returns:
            QuerySet: Список рецептов находящихся в списке покупок
            пользователя.
        """
        if value:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset
