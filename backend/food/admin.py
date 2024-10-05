from django.contrib import admin

from food.models import (
    Ingredients,
    Favourites,
    Tag,
    ShoppingCart,
    Recipe,
    User
)

admin.site.register(Ingredients)
admin.site.register(Tag)
admin.site.register(Recipe)
admin.site.register(User)
admin.site.register(ShoppingCart)
admin.site.register(Favourites)
