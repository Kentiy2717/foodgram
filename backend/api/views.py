from django.db.models import Count, Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from django.urls import reverse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import RecipesPagination
from api.permissions import IsAuthenticatedOwnerOrReadOnly
from api.serializers import (
    AvatarSerializer,
    IngredientsSerializer,
    RecipeSerializer,
    TagSerializer,
    FavouritesSerializer,
    FoodgramUserSerializer,
    SubscribtionsUserSerializer,
    SubscribeCreateSerializer,
    ShoppingCartSerializer
)
from api.services import get_purchased_in_file
from food.models import (
    Ingredients,
    RecipeIngredients,
    Favourites,
    ShoppingCart,
    Tag,
    Recipe,
    User
)
from users.models import Subscribe


class FoodgramUserViewSet(UserViewSet):
    serializer_class = FoodgramUserSerializer
    pagination_class = LimitOffsetPagination

    @action(
        methods=('POST',),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        """Подписка на пользователя."""
        author = get_object_or_404(User, id=id)
        data = {
            'author': author.id,
            'user': request.user.id
        }
        serializer = SubscribeCreateSerializer(
            data=data,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id):
        """Отписка от пользователя."""
        author = get_object_or_404(User, id=id)
        unsubscribe, _ = Subscribe.objects.filter(
            user=request.user,
            author=author.id,
        ).delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
            if unsubscribe
            else status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=('GET',),
        detail=False,
        permission_classes=(IsAuthenticated,),
        pagination_class=None
    )
    def me(self, request):
        serializer = FoodgramUserSerializer(
            request.user,
            context=self.get_serializer_context()
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=('PUT',),
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='me/avatar',
    )
    def put_avatar(self, request):
        serializer = AvatarSerializer(
            instance=self.get_instance(),
            data=request.data,
            partial=True,
            context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @put_avatar.mapping.delete
    def delete_avatar(self, request):
        self.request.user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=('GET',),
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        authors = User.objects.filter(
            subscriptions_on_author__user=request.user
        ).annotate(
            recipes_count=Count('recipes')
        ).order_by('username')
        serializer = SubscribtionsUserSerializer(
            self.paginate_queryset(authors),
            many=True,
            context=self.get_serializer_context()
        )
        return self.get_paginated_response(serializer.data)


class IngredientsViewSet(ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    http_method_names = ('get',)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagsViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ('get',)
    pagination_class = None


class RecipesViewSet(ModelViewSet):
    queryset = Recipe.objects.select_related(
        'author'
    ).all().prefetch_related('tags', 'ingredients')
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = RecipesPagination

    def shopping_cart_favorite_create(self, serializator, pk):
        data = {'user': self.request.user.pk, 'recipe': pk}
        serializator = serializator(
            data=data,
            context={'request': self.request}
        )
        serializator.is_valid(raise_exception=True)
        serializator.save()
        return Response(
            serializator.data,
            status=status.HTTP_201_CREATED
        )

    @action(
        methods=('POST',),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        return self.shopping_cart_favorite_create(
            FavouritesSerializer,
            pk
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        delete, _ = Favourites.objects.filter(
            user=request.user,
            recipe=pk
        ).delete()
        if delete:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=('POST',),
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        return self.shopping_cart_favorite_create(
            ShoppingCartSerializer,
            pk
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        delete, _ = ShoppingCart.objects.filter(
            user=request.user,
            recipe=pk
        ).delete()
        if delete:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=('GET',),
        permission_classes=(IsAuthenticated,),
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        buy = (
            RecipeIngredients.objects.filter(
                recipe__shoppingcart__user=request.user
            )
            .values('ingredients__name', 'ingredients__measurement_unit')
            .annotate(amount=Sum('amount'))
            .order_by('ingredients__name')
        )
        purchased_in_file = '\n'.join(get_purchased_in_file(buy))
        response = FileResponse(purchased_in_file, content_type='text/plain')
        response[
            'Content-Disposition'
        ] = 'attachment; filename=shopping-list.txt'
        return response

    @action(
        detail=True,
        methods=('GET',),
        url_path='get-link',
    )
    def get_link(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        url = request.build_absolute_uri(
            reverse('redirect_link', kwargs={'slug': recipe.short_url})
        )
        return Response({'short-link': url}, status=status.HTTP_200_OK)
