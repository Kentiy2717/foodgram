from django.db import models
from django.contrib.auth import get_user_model

from .constants import (
    MAX_NAME_LENGTH,
    MAX_MEASUREMENT_UNIT_LENGTH
)

User = get_user_model()


class Ingredients(models.Model):  # тут все нормально
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
        # constraints = (  # !!!!! ПРОВЕРЬ ТОЧНО ЛИ ЭТО НУЖНО !!!!!
        #     models.UniqueConstraint(  
        #         fields=['name', 'measurement_unit'],
        #         name='unique_ingredient'
        #     )
        # )

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'  # !!!!! ПРОВЕРЬ ТОЧНО ЛИ ЭТО НУЖНО !!!!!


class Tag(models.Model):  # тут все нормально
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


class Recipe(models.Model):  # тут все нормально
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

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name} ({self.author})'  # !!!!! ПРОВЕРЬ ТОЧНО ЛИ ЭТО НУЖНО !!!!!


class RecipeIngredients(models.Model):  # тут все нормально
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
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        # constraints = (  # !!!!! ПРОВЕРЬ ТОЧНО ЛИ ЭТО НУЖНО !!!!!
        #     models.UniqueConstraint(
        #         fields=('recipe', 'ingredients'),
        #         name='unique_recipe_ingredients'
        #     )
        # )

    def __str__(self):
        return f"{self.recipe.name} - {self.ingredients.name}"


class Favourites(models.Model):  # тут все нормально
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
        # constraints = (  # !!!!! ПРОВЕРЬ ТОЧНО ЛИ ЭТО НУЖНО !!!!!
        #     models.UniqueConstraint(
        #         fields=('user', 'recipe'),
        #         name='unique_favourites'
        #     )
        # )

    def __str__(self):
        return f"{self.user} - {self.recipe}"


class ShoppingCart(models.Model):  # тут все нормально
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
        # constraints = (  # !!!!! ПРОВЕРЬ ТОЧНО ЛИ ЭТО НУЖНО !!!!!
        #     models.UniqueConstraint(
        #         fields=('user', 'recipe'),
        #         name='unique_shopping_cart'
        #     )
        # )
