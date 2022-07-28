from django.contrib.auth import get_user_model
from django.db.models import F
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, Recipe, RecipesIngredients,
                            ShopingCart, Tag)
from users.models import Subscribe

User = get_user_model()

RECIPES_LIMIT = 3


class CustomUserSerialaizer(UserSerializer):
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
        request = self.context.get('request', None)
        if request is None or request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=request.user, author=obj).exists()


class SubscriptionRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(CustomUserSerialaizer):
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
        return SubscriptionRecipeSerializer(
            obj.recipes.all()[:RECIPES_LIMIT], many=True
        ).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscribe
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField()
    measurement_unit = serializers.ReadOnlyField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipesIngredients
        fields = ('id', 'amount')


class RecipeReadSerialaizer(serializers.ModelSerializer):
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
        request = self.context.get('request', None)
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request', None)
        if request is None or request.user.is_anonymous:
            return False
        return ShopingCart.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    def get_ingredients(self, obj):
        ingredients = obj.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('recipe_ingredients__amount')
        )
        return ingredients


class RecipeCreateSerialaizer(serializers.ModelSerializer):
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

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            ingredient_object = Ingredient.objects.get(id=ingredient['id'])
            RecipesIngredients.objects.create(
                recipe=recipe,
                ingredient=ingredient_object,
                amount=ingredient['amount']
            )
        return recipe

    def update(self, recipe, validated_data):

        tags = validated_data.get('tags')
        ingredients = validated_data.get('ingredients')
        recipe.image = validated_data.get('image', recipe.image)
        recipe.name = validated_data.get('name', recipe.name)
        recipe.text = validated_data.get('text', recipe.text)
        recipe.cooking_time = validated_data.get(
            'cooking_time', recipe.cooking_time
        )

        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)

        if ingredients:
            recipe.ingredients.clear()
            for ingredient in ingredients:
                RecipesIngredients.objects.get_or_create(
                    recipe=recipe,
                    ingredient=Ingredient.objects.get(id=ingredient['id']),
                    amount=ingredient['amount']
                )

        recipe.save()
        return recipe

    def to_representation(self, instance):
        return RecipeReadSerialaizer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class FavoriteShopingCartRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('recipe', 'user')

    def to_representation(self, instance):
        return FavoriteShopingCartRecipeSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class ShopingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShopingCart
        fields = ('recipe', 'user')

    def to_representation(self, instance):
        return FavoriteShopingCartRecipeSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
