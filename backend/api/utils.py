from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from recipes.models import Ingredient, Recipe, RecipeIngredient
from rest_framework import status
from rest_framework.response import Response

FAVORITE_EXISTS_MESSAGE = 'Рецепт уже добавлен в избранное'
FAVORITE_MISSING_MESSAGE = 'Рецепт отсутствует в избранном'
SHOPING_CART_EXISTS_MESSAGE = 'Рецепт уже добавлен в список покупок'
SHOPING_CART_MISSING_MESSAGE = 'Рецепт отсутствует в списке покупок'
FROM_FAVORITE = 'избранного у'
FROM_SHOPING_CART = 'списка покупок'
DELETE_MESSAGE = ('Рецепт {recipe} удален '
                  'из {delete_from_message} пользователя {user}')
UNSUBSCRIBE_MESSAGE = 'Пользователь {user} отписался от {author}'
SINGULAR_MUST = 'должен'
PLURAL_MUST = 'должны'
SINGULAR = ''
PLURAL_TAG = 'и'
PLURAL_INGREDIENT = 'ы'
DUPLICATE_MESSAGE = (
    '{element_plural} не должны дублироваться. {element}{ending} '
    '({elements}) {must} быть в единственном числе.'
)
INGREDIENTS = 'ingredients'
INGREDIENT_RU = 'Ингредиент'
INGREDIENTS_RU = 'Ингредиенты'
TAGS = 'tags'
TAG_RU = 'Тег'
TAGS_RU = 'Теги'

RECIPES_LIMIT = 3


def create_delete_object(
        request,
        pk,
        model_serializer,
        model,
        exists_message,
        missing_message,
        delete_from_message
):
    recipe = get_object_or_404(Recipe, id=pk)
    user_id = request.user.id
    serializer = model_serializer(
        data={'user': request.user.id, 'recipe': recipe.id}
    )
    object_exists = model.objects.filter(recipe=pk, user=user_id).exists()
    if request.method == "POST":
        if object_exists:
            return Response(exists_message)
        serializer.is_valid(raise_exception=True)
        serializer.save(recipe=recipe, user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    if not object_exists:
        return Response(missing_message)
    model_object = get_object_or_404(model, user=request.user, recipe__id=pk)
    model_object.delete()
    return Response(
        DELETE_MESSAGE.format(
            recipe=model_object.recipe,
            delete_from_message=delete_from_message,
            user=request.user
        )
    )


def create_recipe_ingredient_objects(recipe, ingredients):
    RecipeIngredient.objects.bulk_create(
        RecipeIngredient(
            recipe=recipe,
            ingredient=get_object_or_404(Ingredient, id=ingredient['id']),
            amount=ingredient['amount']
        ) for ingredient in ingredients
    )


def tags_ingredients_validation(data, element):
    elements = data[element]
    duplicate_objects = [
        obj for obj in elements
        if elements.count(obj) > 1
    ]
    length = len(duplicate_objects)
    plural_ending = PLURAL_INGREDIENT if element == INGREDIENTS else PLURAL_TAG
    if duplicate_objects:
        raise ValidationError(
            DUPLICATE_MESSAGE.format(
                element_plural=(INGREDIENTS_RU if element == INGREDIENTS
                                else TAGS_RU),
                element=INGREDIENT_RU if element == INGREDIENTS else TAG_RU,
                ending=plural_ending if length > 2 else SINGULAR,
                elements=", ".join(
                    set(
                        [get_object_or_404(Ingredient, id=ingredient['id'])
                         .name for ingredient in duplicate_objects]
                    )
                ) if element == INGREDIENTS
                else ", ".join(set([tag.name for tag in duplicate_objects])),
                must=PLURAL_MUST if length > 2 else SINGULAR_MUST
            )
        )
