from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    """Модель для пользователей.

        В качестве логина будет использоваться email, поля ('username',
        'first_name', 'last_name') обязательны к заполнению.

    Attributes:
        username (str): имя пользователя.
        password (str): пароль.
        email (str): электронная почта.
        first_name (str): имя.
        last_name (str): фамилия.
    """

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
        """Возвращает строковое представление модели"""

        return self.username


class Subscribe(models.Model):
    """Модель для хранения подписок.

    Attributes:
        user (int): id пользователя.
        author (int): id автора рецепта.
    """

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
        """Проверяет подписку на самого себя.

        Raises:
            ValidationError: ошибка при попытке подписаться на самого себя.
        """

        if self.user == self.author:
            raise ValidationError('Вы не можете подписаться на самого себя')

    def save(self, *args, **kwargs):
        """Сохраняет модель, предварительно полностью проверив её."""
        self.full_clean()
        return super().save(*args, **kwargs)
