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
NEGATIVE_AMOUNT_MESSAGE = ('Количество ингредиента не может быть '
                           'отрицательным или равно нулю.')
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
    """Добавляет/удаляет рецепт из избранного/списка покупок.

    Args:
        request (Request): объект запроса.
        pk (int): id рецепта.\n
        model_serializer (FavoriteSerializer/ShoppingCartSerializer):
        сериалайзер.
        model (Favorite/ShoppingCart): класс избранного/списка покупок.
        exists_message (str): предупреждение о том что рецепт уже находится в
        избранном/списке покупок.
        missing_message (str): предупреждение о том что рецепт отсутствует в
        избранном/списке покупок.
        delete_from_message (str): сообщение о том откуда удаляется рецепт.

    Returns:
        Если метод запроса "POST":
            Response: сериализованные данные если такого рецепта нету в
            избранном/списке покупок иначе сообщение о том что такой рецепт
            уже присутствует.
        Иначе:
            Response: сообщение о том что рецепт удален из избранного/списка
            покупок иначе сообщение о том что такого рецепта нету в
            избранном/списке покупок.
    """

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
    """Добавляет ингредиенты в рецепт.

    Args:
        recipe (Recipe): объект рецепта.
        ingredients (list): список ингредиентов.
    """

    RecipeIngredient.objects.bulk_create(
        RecipeIngredient(
            recipe=recipe,
            ingredient=get_object_or_404(Ingredient, id=ingredient['id']),
            amount=ingredient['amount']
        ) for ingredient in ingredients
    )


def tags_ingredients_validation(data, element):
    """Проверяет ингредиенты и теги при создании рецепта.

    Args:
        data (dict): словарь с входящими данными.
        element (str): тег или ингредиент.

    Raises:
        ValidationError: ошибка если указано отрицательное количество
        ингредиента.
        ValidationError: ошибка если тег или ингредиент дублируется.
    """

    elements = data[element]
    element_is_ingredient = True if element == INGREDIENTS else False
    if element_is_ingredient:
        ingredients = [
            get_object_or_404(Ingredient, id=ingredient['id']).name
            for ingredient in elements
        ]
        negative_amount = [
            ingredient['amount'] for ingredient in elements
            if ingredient['amount'] <= 0
        ]
        duplicate_objects = [
            ingredient for ingredient in ingredients
            if ingredients.count(ingredient) > 1
        ]
        if negative_amount:
            raise ValidationError(NEGATIVE_AMOUNT_MESSAGE)
    else:
        duplicate_objects = [
            tag for tag in elements
            if elements.count(tag) > 1
        ]
    length = len(duplicate_objects)
    plural_ending = PLURAL_INGREDIENT if element_is_ingredient else PLURAL_TAG
    if duplicate_objects:
        raise ValidationError(
            DUPLICATE_MESSAGE.format(
                element_plural=(INGREDIENTS_RU if element_is_ingredient
                                else TAGS_RU),
                element=INGREDIENT_RU if element_is_ingredient else TAG_RU,
                ending=plural_ending if length > 2 else SINGULAR,
                elements=", ".join(
                    set([ingredient for ingredient in duplicate_objects])
                ) if element_is_ingredient
                else ", ".join(set([tag.name for tag in duplicate_objects])),
                must=PLURAL_MUST if length > 2 else SINGULAR_MUST
            )
        )
