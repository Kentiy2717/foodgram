from django.contrib import admin

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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'ingredients':
            kwargs['queryset'] = Ingredients.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'favorites_count',
    )
    search_fields = ('name', 'author__username',)
    list_filter = ('tags',)
    inlines = (IngredientsInline,)

    def favorites_count(self, obj):
        return obj.favourites.count()


class IngredientsAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(Tag)
admin.site.register(ShoppingCart)
admin.site.register(Favourites)
