from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from api.serializers import RecipeSerializer
from food.models import Recipe


class GetLinkViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    http_method_names = ('get',)

    @action(
        detail=False,
        methods=('get',),
        url_path=r'(?P<short_url>\w+)'
    )
    def redirect_link(self, request, short_url):
        recipe = get_object_or_404(Recipe, short_url=short_url)
        return HttpResponseRedirect(
            request.build_absolute_uri(f'/recipes/{recipe.id}/')
        )
