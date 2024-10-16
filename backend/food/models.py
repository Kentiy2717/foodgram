from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

from food.constants import (
    TOKEN_LENGTH,
    MAX_NAME_LENGTH,
    MAX_NAME_LENGTH_INGREDIENT,
    MAX_NAME_LENGTH_TAG,
    MAX_MEASUREMENT_UNIT_LENGTH,
    MAX_SLUG_LENGTH_TAG,
    MAX_AMOUNT_VALUE,
    MIN_AMOUNT_VALUE
)
from food.services import generate_short_url

User = get_user_model()


class Ingredients(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=MAX_NAME_LENGTH_INGREDIENT
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=MAX_MEASUREMENT_UNIT_LENGTH
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredients'
            ),
        )

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название тега',
        max_length=MAX_NAME_LENGTH_TAG,
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Слаг тега',
        max_length=MAX_SLUG_LENGTH_TAG,
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
        verbose_name='Время приготовления в минутах',
        validators=(MinValueValidator(limit_value=MIN_AMOUNT_VALUE),
                    MaxValueValidator(limit_value=MAX_AMOUNT_VALUE))
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
        generate_short_url(self)
        super().save(*args, **kwargs)


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
        validators=(MinValueValidator(limit_value=MIN_AMOUNT_VALUE),
                    MaxValueValidator(limit_value=MAX_AMOUNT_VALUE))
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredients'),
                name='unique_recipe_ingredients'
            ),
        )

    def __str__(self):
        return f"{self.recipe.name} - {self.ingredients.name}"


class UserRecipeAbstrakt(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)s',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='%(class)s',
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_%(class)s'
            ),
        )

    def __str__(self):
        return f'{self.user} - {self.recipe}. {self._meta.verbose_name}'


class Favourites(UserRecipeAbstrakt):

    class Meta(UserRecipeAbstrakt.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'


class ShoppingCart(UserRecipeAbstrakt):

    class Meta(UserRecipeAbstrakt.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
