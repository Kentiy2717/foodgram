from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SignUpView, UsersViewSet

v1_router = DefaultRouter()
v1_router.register('users', UsersViewSet, basename='users')
v1_router.register('signup', UsersViewSet, basename='users')

v1_auth_urls = [
#     path('', include('djoser.urls')),  # ???
#     path('', include('djoser.urls.jwt')),  # ???
    path('signup/', SignUpView.as_view(), name='signup'),
]


urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/', include(v1_auth_urls)),
]
