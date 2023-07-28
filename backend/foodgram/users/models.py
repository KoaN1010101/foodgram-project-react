from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework.exceptions import ValidationError


class User(AbstractUser):
    username = models.CharField(
        verbose_name='Пользователь',
        max_length=200,
        unique=True
    )
    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=200,
        unique=True
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=200,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=200,
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=200,
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        related_name='subscribing',
        verbose_name='Автор',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def clean(self):
        if self.user == self.author:
            raise ValidationError(
                {'error': 'Невозможно подписаться на себя'}
            )

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'
