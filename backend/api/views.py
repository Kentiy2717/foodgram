from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
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
# from food.utils import download_pdf
from .permissions import IsAdminOrReadOnly, IsAuthenticatedOwnerOrReadOnly
from .serializers import (
    IngredientsSerializer,
    RecipeSerializer,
    TagSerializer,
    FavouritesSerializer,
    FoodgramUserSerializer,
    SubscribtionsUserSerializer,
    SubscribeCreateSerializer,
    ShoppingCartSerializer,
    TokenSerializer
)
from users.models import Subscribe


class FoodgramUserViewSet(UserViewSet):
    serializer_class = FoodgramUserSerializer

    @action(
        methods=['POST'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        '''Подписка на пользователя'''
        author = get_object_or_404(User, id=id)
        data = {'author': author.id}
        serializer = SubscribeCreateSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @subscribe.mapping.delete
    def unsubscribe(self, request, id):
        '''Отписка от пользователя'''
        author = get_object_or_404(User, id=id)
        counter, _ = Subscribe.objects.filter(
            user=request.user,
            author=author.id,
        ).delete()
        if counter == 0:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

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
    
    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        subscribtions = Subscribe.objects.filter(user=request.user)
        authors = User.objects.filter(author_subscription__in=subscribtions)
        serializer = SubscribtionsUserSerializer(
            self.paginate_queryset(authors),
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


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
        serializator = serializator(
            data={'user': user.pk, 'recipe': recipe.pk}
        )
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
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        shopping_cart = ShoppingCart.objects.filter(user=self.request.user)
        recipes = [item.recipe.id for item in shopping_cart]
        buy = (
            RecipeIngredients.objects.filter(recipe__in=recipes)
            .values('ingredients')
            .annotate(amount=Sum('amount'))
        )
        purchased = [
            "Список покупок:",
        ]
        for item in buy:
            ingredient = Ingredients.objects.get(pk=item["ingredients"])
            amount = item["amount"]
            purchased.append(
                f"{ingredient.name}: {amount}, "
                f"{ingredient.measurement_unit}"
            )
        purchased_in_file = "\n".join(purchased)
        response = HttpResponse(purchased_in_file, content_type="text/plain")
        response[
            "Content-Disposition"
        ] = "attachment; filename=shopping-list.txt"
        return response
    
    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
        url_path='(?P<pk>[^/.]+)/get-link',
    )
    def get_link(self, request):
        serializer = TokenSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            token, status_code = serializer.create(
                validated_data=serializer.validated_data
            )
            return Response(TokenSerializer(token).data, status=status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

#     def get_link(self, request):
#         short_link = get_short_link(request)
#         return Response({'short_link': short_link})
# return HttpResponseRedirect(
#             request.build_absolute_uri(
#                 f'/recipes/{recipe.id}'
#                 # reverse('api:recipes-detail', kwargs={'pk': recipe.id})
#             )
#         )