from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from food.filters import IngredientFilter, RecipeFilter
from food.models import (
    Ingredients,
    RecipeIngredients,
    Favourites,
    ShoppingCart,
    Tag,
    Recipe,
    User
)

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
from users.models import Subscribe


class FoodgramUserViewSet(UserViewSet):
    serializer_class = FoodgramUserSerializer
    pagination_class = LimitOffsetPagination

    @action(
        methods=['POST'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        """Подписка на пользователя."""
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
        """Отписка от пользователя."""
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
        serializer = AvatarSerializer(
            instance=self.get_instance(),
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


class IngredientsViewSet(ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    http_method_names = ('get',)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagsViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ('get',)
    pagination_class = None


class RecipesViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = RecipesPagination

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
        if self.request.method == 'DELETE':
            return Response(
                {'errors': 'Рецепта нет в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST
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
        detail=True,
        methods=('get',),
        url_path='get-link',
    )
    def get_link(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        url = request.build_absolute_uri(
            f'/s/{recipe.short_url}'
        )
        return Response({'short-link': url}, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=('get',),
        url_path=r's/(?P<short_url>\w+)'
    )
    def redirect_link(self, request, short_url):
        recipe = get_object_or_404(Recipe, short_url=short_url)
        return HttpResponseRedirect(
            request.build_absolute_uri(f'/recipes/{recipe.id}/')
        )
