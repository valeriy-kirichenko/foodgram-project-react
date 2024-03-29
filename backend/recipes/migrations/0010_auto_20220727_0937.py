# Generated by Django 2.2.28 on 2022-07-27 06:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0009_auto_20220727_0935'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='favorite',
            constraint=models.UniqueConstraint(fields=('recipe', 'user'), name='favorite_unique'),
        ),
        migrations.AddConstraint(
            model_name='shopingcart',
            constraint=models.UniqueConstraint(fields=('recipe', 'user'), name='shoping_cart_unique'),
        ),
    ]
