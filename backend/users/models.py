"""Модель пользователя."""

from django.db import models
from django.contrib.auth.models import AbstractUser

from .constants import NAME_MAX_LENGTH, EMAIL_MAX_LENGTH
from api.validators import validate_username


class User(AbstractUser):
    """Модель пользователя."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
        'password'
    )

    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=EMAIL_MAX_LENGTH,
        unique=True
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=NAME_MAX_LENGTH,
        unique=True,
        validators=(validate_username,),
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=NAME_MAX_LENGTH
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=NAME_MAX_LENGTH
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=NAME_MAX_LENGTH
    )
    is_staff = models.BooleanField(
        verbose_name='Статус персонала',
        default=False
    )
    is_subscribed = models.BooleanField(
        verbose_name='Статус подписки',
        default=False
    )
    avatar = models.ImageField(
        verbose_name='Аватар',
        upload_to='users/',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='Subscriber',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author_subscription',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscription'
            ),
        )
