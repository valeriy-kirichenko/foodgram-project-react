# Generated by Django 2.2.28 on 2022-07-25 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_auto_20220723_1757'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='favorite',
            name='recipe_unique',
        ),
        migrations.AddConstraint(
            model_name='favorite',
            constraint=models.UniqueConstraint(fields=('recipe', 'user'), name='favorite_unique'),
        ),
        migrations.AddConstraint(
            model_name='shopingcart',
            constraint=models.UniqueConstraint(fields=('recipe', 'user'), name='shoping_cart_unique'),
        ),
    ]