from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        verbose_name = 'Пользователь',
        max_length=200,
        unique=True
    )
    email = models.EmailField(
        verbose_name = 'Электронная почта',
        max_length=200,
        unique=True
    )
    first_name = models.CharField(
        verbose_name = 'Имя',
        max_length=200,
        unique=True
    )
    last_name = models.CharField(
        verbose_name = 'Фамилия',
        max_length=200,
        unique=True
    )
    password = models.CharField(
        verbose_name = 'Пароль',
        max_length=200,
        unique=True
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
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name ='Подписчик'
    )
    author = models.ForeignKey(
        User,
        related_name='subscribing',
        verbose_name='Автор',
        on_delete=models.CASCADE,
    )
