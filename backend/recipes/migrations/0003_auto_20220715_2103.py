# Generated by Django 2.2.28 on 2022-07-15 18:03

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20220715_2034'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ingredient',
            name='amount',
        ),
        migrations.AddField(
            model_name='recipesingredients',
            name='amount',
            field=models.IntegerField(default=1, help_text='Введите количество', validators=[django.core.validators.MinValueValidator(1)], verbose_name='Количество'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
    ]
