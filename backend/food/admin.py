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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'ingredients':
            kwargs['queryset'] = Ingredients.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientsInline,)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredients)
admin.site.register(Tag)
admin.site.register(ShoppingCart)
admin.site.register(Favourites)
