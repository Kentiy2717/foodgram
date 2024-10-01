from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from food.filters import IngredientFilter, RecipeFilter, Recipe
from food.models import (
    Ingredients,
    RecipeIngredients,
    Favourites,
    ShoppingCart,
    Tag,
    Recipe,
    User
)
from food.utils import download_pdf
from .permissions import IsAdminOrReadOnly, IsAuthenticatedOwnerOrReadOnly
from .serializers import (
    IngredientsSerializer,
    RecipeSerializer,
    TagSerializer,
    FoodgramUserSerializer,
    SubscribeListSerializer,
    SubscribeRecipeSerializer,
    SubscribeCreateSerializer,
    ShoppingCartSerializer,
    FavouritesSerializer
)
from users.models import Subscribe


class FoodgramUserViewSet(UserViewSet):
    serializer_class = FoodgramUserSerializer

    @action(
        methods=['POST'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, **kwargs):
        '''Подписка на пользователя'''
        id = kwargs.get('pk')
        author = get_object_or_404(User, id=id)
        user = self.request.user
        data = {'user': user.id, 'author': id}
        serializer = SubscribeCreateSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        subscribe = Subscribe.objects.create(user=user, author=author)
        serializer = SubscribeCreateSerializer(
            subscribe,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @subscribe.mapping.delete
    def unsubscribe(self, request, **kwargs):
        '''Отписка от пользователя'''
        id = kwargs.get('pk')
        author = get_object_or_404(User, id=id)
        user = self.request.user
        subscribe = Subscribe.objects.filter(user=user, author=author)
        if subscribe.exists():
            subscribe.delete()
            return Response(
                {'detail': 'Вы отписались от этого пользователя'},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {'detail': 'Вы не были подписаны на этого пользователя'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        pagination_class=None
    )
    def me(self, request):
        serializer = FoodgramUserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(
        methods=['PUT'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='me/avatar',
    )
    def put_avatar(self, request):
        serializer = FoodgramUserSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @put_avatar.mapping.delete
    def delete_avatar(self, request):
        user = self.get_instance()
        if user.avatar:
            user.avatar.delete()
            user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# class AvatarViewSet(APIView):
#     permission_classes = [IsAuthenticated]
# 
#     def put(self, request):
#         serializer = FoodgramUserSerializer(
#             request.user,
#             data=request.data,
#             partial=True
#         )
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
#     
#     def delete(self, request):
#         return Response({'success': 'Avatar deleted'})


class IngredientsViewSet(ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    http_method_names = ('get',)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter

#     def post(self, request, *args, **kwargs):
#         serializer = IngredientsSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)


# class RecipesViewSet(ModelViewSet):
#     queryset = Recipe.objects.all()
#     serializer_class = RecipeSerializer
#     http_method_names = ('get', 'patch', 'post', 'delete')
# 
#     def post(self, request, *args, **kwargs):
#         serializer = RecipeSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)


class TagsViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ('get',)
    pagination_class = None

#     def post(self, request, *args, **kwargs):
#         serializer = TagSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)


class RecipesViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def shopping_cart_favorite_hendler(self, model, serializator, recipe):
        user = self.request.user
        serializator = serializator(data={'user': user.pk, 'recipe': recipe.pk})
        if model.objects.filter(user=user, recipe=recipe).exists():
            if self.request.method == 'POST':
                return Response(
                    {'errors': 'Рецепт уже в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            object_recipe = get_object_or_404(model, user=user, recipe=recipe)
            object_recipe.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )
        serializator.is_valid(raise_exception=True)
        serializator.save()
        return Response(
            serializator.data,
            status=status.HTTP_201_CREATED
        )

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        return self.shopping_cart_favorite_hendler(
            Favourites,
            FavouritesSerializer,
            recipe
        )

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        return self.shopping_cart_favorite_hendler(
            ShoppingCart,
            ShoppingCartSerializer,
            recipe
        )

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients_obj = (
            RecipeIngredients.objects.filter(recipe__carts__user=request.user)
            .values('ingredients__name', 'ingredients__measurement_unit')
            .annotate(sum_amount=Sum('amount'))
        )
        data_dict = {}
        ingredients_list = []
        for item in ingredients_obj:
            name = item['ingredients__name'].capitalize()
            unit = item['ingredients__measurement_unit']
            sum_amount = item['sum_amount']
            data_dict[name] = [sum_amount, unit]
        for ind, (key, value) in enumerate(data_dict.items(), 1):
            if ind < 10:
                ind = '0' + str(ind)
            ingredients_list.append(
                f'{ind}. {key} - ' f'{value[0]} ' f'{value[1]}'
            )
        return download_pdf(ingredients_list)


class SubscribeListView(generics.ListAPIView):
    '''Список подписок.'''
    queryset = User.objects.all()
    serializer_class = SubscribeListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return User.objects.filter(author_subscription__user=self.request.user)
