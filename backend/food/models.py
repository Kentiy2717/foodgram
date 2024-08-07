from django.db import models
from django.contrib.auth import get_user_model

from .constants import MAX_NAME_LENGTH, MAX_MEASUREMENT_UNIT_LENGTH


User = get_user_model()


# class Ingredients(models.Model):
#     name = models.CharField(
#         verbose_name='Название ингредиента',
#         max_length=MAX_NAME_LENGTH
#     )
#     measurement_unit = models.CharField(
#         verbose_name='Единица измерения',
#         max_length=MAX_MEASUREMENT_UNIT_LENGTH
#     )
# 
#     class Meta:
#         verbose_name = 'Ингредиент'
#         verbose_name_plural = 'Ингредиенты'
#         required = ('id',)
# 
#     def __str__(self):
#         return self.name
# 
# 
# class Tag(models.Model):
#     name = models.CharField(
#         verbose_name='Название тега',
#         max_length=MAX_NAME_LENGTH
#     )
#     slug = models.SlugField(
#         verbose_name='Слаг тега',
#         unique=True
#     )
# 
#     class Meta:
#         verbose_name = 'Тег'
#         verbose_name_plural = 'Теги'
#         required = ('id',)
# 
#     def __str__(self):
#         return self.name
# 
# 
# class Recipe(models.Model):
#     ingredients = models.ManyToManyField(
#         Ingredients,
#         verbose_name='Ингредиенты',
#         related_name='recipes'
#     )
#     tags = models.ManyToManyField(
#         Tag,
#         verbose_name='Теги',
#         related_name='recipes'
#     )
#     image = models.ImageField(
#         verbose_name='Изображение',
#         upload_to='recipes/images/'
#     )
#     name = models.CharField(
#         verbose_name='Название рецепта',
#         max_length=MAX_NAME_LENGTH
#     )
#     text = models.TextField(
#         verbose_name='Описание рецепта'
#     )
#     cooking_time = models.PositiveSmallIntegerField(
#         verbose_name='Время приготовления в минутах'
#     )
#     author = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name='recipes',
#         verbose_name='Автор'
#     )
#     is_favorite = models.BooleanField(
#         verbose_name='Избранное',
#         default=False
#     )
#     is_in_shopping_cart = models.BooleanField(
#         verbose_name='В корзине',
#         default=False
#     )
# 
#     class Meta:
#         verbose_name = 'Рецепт'
#         verbose_name_plural = 'Рецепты'
#         required = (
#             'id',
#             'ingredients',
#             'tags',
#             'image',
#             'name',
#             'text',
#             'cooking_time',
#         )
# 
#     def __str__(self):
#         return self.name