from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
        help_text='Введите имя пользователя'
    )
    password = models.CharField(
        'Пароль', max_length=254, help_text='Введите пароль'
    )
    email = models.EmailField(
        'Электронная почта',
        unique=True,
        max_length=254,
        help_text='Введите электронную почту'
    )
    first_name = models.CharField(
        'Имя', max_length=150, help_text='Введите имя'
    )
    last_name = models.CharField(
        'Фамилия', max_length=150, help_text='Введите фамилию'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='follower',
        on_delete=models.CASCADE
    )

    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='following',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'), name='unique_subscribe'
            ),
        )

    def clean(self):
        if self.user == self.author:
            raise ValidationError('Вы не можете подписаться на самого себя')

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
