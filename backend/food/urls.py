from django.urls import include, path
from rest_framework.routers import DefaultRouter

from food.views import GetLinkViewSet

v1_router = DefaultRouter()
v1_router.register('s', GetLinkViewSet, basename='get_link')

urlpatterns = [
    path('', include(v1_router.urls)),
]
