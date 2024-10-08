import random

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

from food.constants import (
    CHARACTERS,
    TOKEN_LENGTH,
    MAX_NAME_LENGTH,
    MAX_MEASUREMENT_UNIT_LENGTH,
    MAX_AMOUNT_VALUE,
    MIN_AMOUNT_VALUE
)

User = get_user_model()


class Ingredients(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=MAX_NAME_LENGTH
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=MAX_MEASUREMENT_UNIT_LENGTH
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название тега',
        max_length=MAX_NAME_LENGTH,
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Слаг тега',
        max_length=MAX_NAME_LENGTH,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=MAX_NAME_LENGTH
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/images/'
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        verbose_name='Ингредиенты',
        related_name='recipes',
        through='RecipeIngredients'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    short_url = models.CharField(
        max_length=TOKEN_LENGTH,
        unique=True,
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name} ({self.author})'

    def save(self, *args, **kwargs):
        if not self.short_url:
            while True:
                self.short_url = ''.join(
                    random.choices(
                        CHARACTERS,
                        k=TOKEN_LENGTH
                    )
                )
                if not Recipe.objects.filter(
                    short_url=self.short_url
                ).exists():
                    break
        super().save(*args, **kwargs)

#     def clean(self):
#         if self.ingredients.count() == 0:
#             raise ValidationError(
#                 'Нужен хотя бы один ингредиент'
#             )


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт'
    )
    ingredients = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(limit_value=MIN_AMOUNT_VALUE),
                    MaxValueValidator(limit_value=MAX_AMOUNT_VALUE)]
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'

    def __str__(self):
        return f"{self.recipe.name} - {self.ingredients.name}"


class Favourites(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favourites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favourites',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'

    def clean(self):
        if Favourites.objects.filter(
            user=self.user,
            recipe=self.recipe
        ).exists():
            raise ValidationError(
                'Рецепт уже добавлен в избранное.'
            )

    def __str__(self):
        return f"{self.user} - {self.recipe}"


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def clean(self):
        if ShoppingCart.objects.filter(
            user=self.user,
            recipe=self.recipe
        ).exists():
            raise ValidationError(
                'Рецепт уже добавлен в список покупок.'
            )
