# Generated by Django 2.2.28 on 2022-07-27 06:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_auto_20220725_2012'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='favorite',
            name='favorite_unique',
        ),
        migrations.RemoveConstraint(
            model_name='shopingcart',
            name='shoping_cart_unique',
        ),
    ]
