from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view

from food.models import Recipe


@api_view(['GET'])
def redirect_link(request, slug):
    """Возвращает рецепт по его коротной ссылке."""
    recipe = get_object_or_404(Recipe, short_url=slug)
    return HttpResponseRedirect(
        request.build_absolute_uri(f'/recipes/{recipe.id}/')
    )
