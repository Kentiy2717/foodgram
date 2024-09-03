from django.contrib import admin

from food.models import Ingredients, Tag, Recipe, User

admin.site.register(Ingredients)
admin.site.register(Tag)
admin.site.register(Recipe)
# admin.site.register(RecipeIngredients)
admin.site.register(User)


# from django.contrib import admin
# 
# from food.models import (
#     Ingredients, Recipe, Tag, RecipeIngredients, ShoppingCart, Favourites
# )
# 
# 
# @admin.register(Tag)
# class TagAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name', 'slug', 'color')
#     list_editable = ('color',)
#     list_display_links = ('name',)
#     search_fields = ('name',)
# 
# 
# @admin.register(Ingredients)
# class IngredientAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name', 'measurement_unit')
#     list_filter = ('name', )
#     list_display_links = ('name',)
#     search_fields = ('name', )
#     empty_value_display = '-пусто-'
# 
# 
# class RecipeIngredientInline(admin.TabularInline):
#     model = Recipe.ingredients.through
#     extra = 1
# 
# 
# @admin.register(Recipe)
# class RecipeAdmin(admin.ModelAdmin):
#     list_display = (
#         'id', 'name', 'author', 'text', 'cooking_time', 'pub_date', 'image',
#     )
#     list_filter = ('name', 'author', 'tags')
#     ordering = ('-pub_date',)
#     inline = (RecipeIngredientInline, )
#     readonly_fields = ('favorite_count', 'pub_date')
#     list_display_links = ('name',)
#     search_fields = ('name',)
# 
#     @admin.display(description='Кол-во добавлений в избранное')
#     def favorite_count(self, recipe):
#         return recipe.favorites_recipe.count()
# 
# 
# @admin.register(RecipeIngredients)
# class IngredientRecipeAdmin(admin.ModelAdmin):
#     list_display = ('id', 'recipe', 'ingredient', 'amount')
#     list_display_links = ('recipe',)
#     search_fields = ('recipe',)
# 
# 
# @admin.register(Favourites)
# class FavoriteAdmin(admin.ModelAdmin):
#     list_display = ('id', 'user', 'recipe')
#     list_display_links = ('user',)
#     search_fields = ('user',)
# 
# 
# @admin.register(ShoppingCart)
# class ShoppingCartAdmin(admin.ModelAdmin):
#     list_display = ('id', 'user', 'recipe')
#     list_display_links = ('user',)
#     search_fields = ('user',)