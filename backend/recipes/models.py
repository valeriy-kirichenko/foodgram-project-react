from django.core.validators import MinValueValidator
from django.db import models
from users.models import User
from utils import COLOR_CHOICES


class RecipeIngredient(models.Model):
    """Модель для связи ингредиентов с рецептами.

    Attributes:
        recipe (int): id рецепта.
        ingredient (int): id ингредиента.
        amount (int): количество ингредиента в рецепте.
    """

    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        'Ingredient',
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Ингредиенты'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        default=1,
        help_text='Введите количество',
        validators=(MinValueValidator(1),)
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='recipe_ingredient_unique'
            ),
        ]
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        """Возвращает строковое представление модели"""

        return (f'{self.ingredient.name}: {self.amount},'
                f' {self.ingredient.measurement_unit}')


class Ingredient(models.Model):
    """Модель для ингредиентов.

    Attributes:
        name (str): название ингредиента.
        measurement_unit (str): единицы измерения.
    """

    name = models.CharField('Название', max_length=200)
    measurement_unit = models.CharField('Единица измерения', max_length=200)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        """Возвращает строковое представление модели"""

        return self.name


class Tag(models.Model):
    """Модель для тегов.

    Attributes:
        name (str): название тега.
        color (str): цвет окраски тега (HEX-код).
        slug (str): уникальное название латиницей.
    """

    name = models.CharField('Название', max_length=200, unique=True,)
    color = models.CharField(
        'Цветовой HEX-код', max_length=7, unique=True, choices=COLOR_CHOICES
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Уникальное название латиницей'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        """Возвращает строковое представление модели"""

        return self.name


class Recipe(models.Model):
    """Модель для рецептов.

    Attributes:
        name (str): название рецепта.
        text (str): текст рецепта.
        image (str): изображение (путь до него).
        cooking_time (int): время готовки.
        pub_date (datetime): дата создания рецепта.
        ingredients (int): ингредиенты (связь ManyToMany, через модель
        RecipeIngredient).
        tags (int): теги (связь ManyToMany).
        author (int): id автора рецепта.
    """

    name = models.CharField(
        'Название',
        max_length=200,
        help_text='Введите название рецепта'
    )
    text = models.TextField(
        'Текст',
        help_text='Опишите здесь свой рецепт'
    )
    image = models.ImageField('Картинка', upload_to='recipes/')
    cooking_time = models.PositiveSmallIntegerField(
        'Время готовки',
        help_text='Введите время готовки',
        validators=(MinValueValidator(1),)
    )
    pub_date = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
        db_index=True
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиент',
        through='RecipeIngredient',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
        related_name='recipes'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        """Возвращает строковое представление модели"""

        return self.name


class ShoppingCart(models.Model):
    """Модель для списка покупок.

    Attributes:
        user (int): id пользователя.
        recipe (int): id рецепта.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='shoping_cart_unique'
            ),
        ]
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'


class Favorite(models.Model):
    """Модель для избранного.

    Attributes:
        user (int): id пользователя.
        recipe (int): id рецепта.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='favorite_unique'
            ),
        ]
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
