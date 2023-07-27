from django.contrib.auth.models import AbstractUser
from django.db import models


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
        ordering = ('id',)
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
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'
