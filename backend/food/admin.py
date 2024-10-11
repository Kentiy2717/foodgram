from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

from food.models import (
    Ingredients,
    Favourites,
    Tag,
    ShoppingCart,
    Recipe,
    RecipeIngredients,
)


class IngredientsInline(admin.StackedInline):
    model = RecipeIngredients
    extra = 1
    min_num = 1

#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         if db_field.name == 'ingredients':
#             kwargs['queryset'] = Ingredients.objects.all()
#         return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'image_preview',
        'name',
        'author',
        'favorites_count',
        'ingredients_list',
        'tags_list',
    )
    search_fields = ('name', 'author__username',)
    list_filter = ('tags',)
    inlines = (IngredientsInline,)

    @admin.display(description='Изображение')
    def image_preview(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="100" />')

    @admin.display(description='Количество в избранном')
    def favorites_count(self, obj):
        return obj.favourites.count()
    
    @admin.display(description='Ингредиенты')
    def ingredients_list(self, obj):
        return ', '.join([
            ingredient.name for ingredient in obj.ingredients.all()
        ])

    @admin.display(description='Теги')
    def tags_list(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()])


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )


@admin.register(Favourites)
class FavouritesAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )


admin.site.unregister(Group)
