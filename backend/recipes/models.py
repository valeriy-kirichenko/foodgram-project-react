from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class RecipesIngredients(models.Model):
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
    amount = models.IntegerField(
        'Количество',
        default=1,
        help_text='Введите количество',
        validators=(MinValueValidator(1),),
        null=False,
        blank=True
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
        return (f'{self.ingredient.name}: {self.ingredient.amount},'
                f' {self.ingredient.measurement_unit}')


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=200,)
    amount = models.IntegerField(
        'Количество',
        default=1,
        help_text='Введите количество',
        validators=(MinValueValidator(1),),
        null=False,
        blank=True
    )
    measurement_unit = models.CharField('Единица измерения',  max_length=200,)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    BLUE = '#0000FF'
    ORANGE = '#FFA500'
    GREEN = '#008000'
    PURPLE = '#800080'
    YELLOW = '#FFFF00'

    COLOR_CHOICES = [
        (BLUE, 'Синий'),
        (ORANGE, 'Оранжевый'),
        (GREEN, 'Зеленый'),
        (PURPLE, 'Фиолетовый'),
        (YELLOW, 'Желтый'),
    ]
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
        return self.name


class Recipe(models.Model):
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
    cooking_time = models.IntegerField(
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
        through='RecipesIngredients',
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
        ordering = ('name',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class ShopingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopingcart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopingcart',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'


class Favorite(models.Model):
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
                name='recipe_unique'
            ),
        ]
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
