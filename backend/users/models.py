"""Модель пользователя."""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

from .constants import EMAIL_MAX_LENGTH


class User(AbstractUser):
    """Модель пользователя."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name'
    )

    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=EMAIL_MAX_LENGTH,
        unique=True
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

    def clean(self):
        if self.user == self.author:
            raise ValidationError(
                'Нельзя подписаться на себя.'
            )
