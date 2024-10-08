from django.urls import include, path
from rest_framework.routers import DefaultRouter

# from food.views import GetLinkView
from food.views import GetLinkViewSet

# urlpatterns = [
#     path('', GetLinkView.as_view(), name='get_link'),
# ]

v1_router = DefaultRouter()
v1_router.register('s', GetLinkViewSet, basename='get_link')

urlpatterns = [
    path('', include(v1_router.urls)),
]
