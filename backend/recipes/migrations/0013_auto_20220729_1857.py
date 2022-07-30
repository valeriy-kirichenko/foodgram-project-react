# Generated by Django 2.2.28 on 2022-07-29 15:57

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0012_auto_20220728_2037'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='RecipesIngredients',
            new_name='RecipeIngredient',
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(help_text='Введите время готовки', validators=[django.core.validators.MinValueValidator(1)], verbose_name='Время готовки'),
        ),
    ]
