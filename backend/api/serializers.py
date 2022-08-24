from django.db.models import F
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework import serializers
from users.models import Subscribe, User

from .utils import (INGREDIENTS, RECIPES_LIMIT, TAGS,
                    create_recipe_ingredient_objects,
                    tags_ingredients_validation)


class CustomUserSerialaizer(UserSerializer):
    """Сериализатор для вывода данных пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        """Проверяет подписку на пользователя.

        Args:
            obj (User): объект пользователя.

        Returns:
            bool: статус подписки.
        """
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=request.user, author=obj).exists()


class SubscriptionRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для вывода списка рецептов пользователя на которого
    подписан текущий пользователь.
    """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(CustomUserSerialaizer):
    """Сериалайзер для вывода списка подписок текущего пользователя."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        """Возвращает сериализованный список рецептов пользователя на которого
        подписан текущий пользователь.

        Args:
            obj (User): объект пользователя на которого подписан текущий
            пользователь.

        Returns:
            rest_framework.utils.serializer_helpers.ReturnList: сериализованный
            список рецептов пользователя на которого подписан текущий
            пользователь.
        """

        return SubscriptionRecipeSerializer(
            obj.recipes.all()[:RECIPES_LIMIT], many=True
        ).data

    def get_recipes_count(self, obj):
        """Возвращает общее количество рецептов пользователя.

        Args:
            obj (User): объект пользователя.

        Returns:
            int: общее количество рецептов пользователя.
        """

        return Recipe.objects.filter(author=obj).count()


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериалайзер для работы с подписками(создание, удаление)."""

    class Meta:
        model = Subscribe
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для вывода списка тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для вывода списка ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для вывода списка ингредиентов в рецепте."""

    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeReadSerialaizer(serializers.ModelSerializer):
    """Сериалайзер для вывода списка рецептов."""

    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    author = CustomUserSerialaizer()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        """Проверяет наличие рецепта в избранном у текущего пользователя.

        Args:
            obj (Recipe): обьект рецепта.

        Returns:
            bool: False если ключ 'request' отсутствует в словаре контекста или
            пользователь не авторизован.

        Для авторизованного пользователя:

        Returns:
            bool: True если рецепт находится в избранном у текущего
            пользователя, иначе False.
        """

        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверяет наличие рецепта в списке покупок текущего пользователя.

        Args:
            obj (Recipe): обьект рецепта.

        Returns:
            bool: False если ключ 'request' отсутствует в словаре контекста или
            пользователь не авторизован.

        Для авторизованного пользователя:

        Returns:
            bool: True если рецепт находится в списке покупок текущего
            пользователя, иначе False.
        """

        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    def get_ingredients(self, obj):
        """Возвращает список ингредиентов.

        Args:
            obj (Reipe): объект рецепта.

        Returns:
            QuerySet: список ингредиентов.
        """

        return obj.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('recipe_ingredients__amount')
        )


class RecipeCreateSerialaizer(serializers.ModelSerializer):
    """Сериалайзер для создания рецепта."""

    ingredients = IngredientRecipeSerializer(many=True)
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'ingredients',
            'image',
            'name',
            'text',
            'cooking_time'
        )

    def validate(self, data):
        """Валидация ингредиентов и тегов.

        Args:
            data (dict): словарь с данными для валидации.

        Returns:
            dict: словарь с данными прошедшими валидацию.
        """

        tags_ingredients_validation(data, INGREDIENTS)
        tags_ingredients_validation(data, TAGS)
        return super().validate(data)

    def create(self, validated_data):
        """Создание рецепта.

        Args:
            validated_data (dict): словарь с данными прошедшими валидацию.

        Returns:
            Recipe: объект рецепта.
        """

        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        create_recipe_ingredient_objects(
            recipe, ingredients
        )
        return recipe

    def update(self, recipe, validated_data):
        """Обновление рецепта.

        Args:
            recipe (Recipe): объект рецепта.
            validated_data (dict): словарь с данными прошедшими валидацию.

        Returns:
            Возвращает метод .update() родительского класса.
        """
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe.tags.set(tags)
        if ingredients:
            recipe.ingredients.clear()
            create_recipe_ingredient_objects(recipe, ingredients)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        """Возвращает словарь с данными о созданном рецепте.

        Args:
            instance (Recipe): объект рецепта.

        Returns:
            dict: словарь с данными о созданном рецепте.
        """
        return RecipeReadSerialaizer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class FavoriteShoppingCartRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для рецепта добавленного в избранное/список покупок."""

    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериалайзер для добавления рецепта в избранное."""

    class Meta:
        model = Favorite
        fields = ('recipe', 'user')

    def to_representation(self, instance):
        """Возвращает словарь с данными о рецепте добавленном в избранное.

        Args:
            instance (Recipe): объект рецепта.

        Returns:
            dict: словарь с данными о рецепте добавленном в избранное.
        """

        return FavoriteShoppingCartRecipeSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериалайзер для добавления рецепта в список покупок."""

    class Meta:
        model = ShoppingCart
        fields = ('recipe', 'user')

    def to_representation(self, instance):
        """Возвращает словарь с данными о рецепте добавленном в список покупок.

        Args:
            instance (Recipe): объект рецепта.

        Returns:
            dict: словарь с данными о рецепте добавленном в список покупок.
        """

        return FavoriteShoppingCartRecipeSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
