from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    IngredientsViewSet,
    RecipesViewSet,
    TagsViewSet,
    AvatarViewSet,
)


v1_router = DefaultRouter()
v1_router.register('ingredients', IngredientsViewSet, basename='ingredients')
v1_router.register('recipes', RecipesViewSet, basename='recipes')
v1_router.register('tags', TagsViewSet, basename='tags')

v1_auth_urls = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/me/avatar/', AvatarViewSet.as_view(), name='avatar'),
]


urlpatterns = [
    path('', include(v1_router.urls)),
    path('', include(v1_auth_urls)),
]
