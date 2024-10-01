import base64

from django.db import transaction
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from rest_framework.permissions import IsAuthenticated, AllowAny

from food.models import (
    Ingredients,
    Favourites,
    Recipe,
    RecipeIngredients,
    ShoppingCart,
    Tag,
    User
)
from users.models import Subscribe
from .validators import validate_username
from users.constants import NAME_MAX_LENGTH, EMAIL_MAX_LENGTH


class Base64ImageField(serializers.ImageField):
    """Сериализатор для картинок."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext) 
        return super().to_internal_value(data)


class FoodgramUserSerializer(UserSerializer):  # тут все нормально
    """Сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=request.user, author=obj).exists()

#     def get_avatar(self, obj):  # Это точно надо?
#         return obj.avatar.url if obj.avatar else None

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed',
            'avatar',
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, data):
        if User.objects.filter(username=data.get('username'),
                               email=data.get('email')):
            return data
        if User.objects.filter(username=data.get('username')):
            raise ValidationError(
                'Пользователь с таким username уже существует.'
            )
        if User.objects.filter(email=data.get('email')):
            raise ValidationError(
                'Пользователь с таким email уже существует.'
            )
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            password=validated_data.get('password')
        )
        user.save()
        return user


class SubscribeCreateSerializer(serializers.ModelSerializer):  # тут все нормально
    """Сериализатор подписки."""

    user = serializers.SlugRelatedField(
        slug_field='id',
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )
    author = serializers.SlugRelatedField(
        slug_field='id',
        queryset=User.objects.all(),
    )

    def validate(self, data):
        if (data['user'] == data['author'] and self.context['request'].method == 'POST'):
            raise serializers.ValidationError(
                'Нельзя подписаться на себя.'
            )
        return data

    class Meta:
        model = Subscribe
        fields = (
            'user',
            'author',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого пользователя.'
            )
        ]


class SubscribeListSerializer(serializers.ModelSerializer):  # тут все нормально
    """Сериализатор подписки."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True
    )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=request.user, author=obj).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        author = get_object_or_404(User, id=obj.id)
        recipes = Recipe.objects.filter(author=author)
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        serializers = SubscribeRecipeSerializer(
            recipes,
            many=True,
            context={'request': request}
        )
        return serializers.data

    class Meta:
        model = Subscribe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
        # read_only_fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeRecipeSerializer(serializers.ModelSerializer):  # тут все нормально
    """Сериализатор подписки."""

    class Meta:
        model = Subscribe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
        # read_only_fields = ('id', 'name', 'image', 'cooking_time')  # надо?


class TagSerializer(serializers.ModelSerializer):  # тут все нормально
    """Сериализатор тега."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'slug',
        )
        # read_only_fields = ('id', 'name', 'slug', 'color')


class IngredientsSerializer(serializers.ModelSerializer):  # тут все нормально
    """Сериализатор ингредиента."""

    class Meta:
        model = Ingredients
        fields = (
            'id',
            'name',
            'measurement_unit',
        )
#         read_only_fields = ('id', 'name', 'measurement_unit')  # надо?


class IngredientsCreateSerializer(serializers.ModelSerializer):  # тут все нормально
    """Сериализатор создания ингредиента."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all()
    )

    class Meta:
        model = RecipeIngredients
        fields = (
            'id',
            'amount',
        )
        # read_only_fields = ('id', 'recipe')  # это точно нужно?


class RecipeIngredientsSerializer(serializers.ModelSerializer):  # тут все нормально
    """Сериализатор ингредиентов рецепта."""

    # id = serializers.PrimaryKeyRelatedField(
    #     queryset=Ingredients.objects.all()
    # )
    id = serializers.IntegerField(
        source='ingredients.id'
    )
    measurement_unit = serializers.ReadOnlyField(  # в гугле CharField 
        source='ingredients.measurement_unit'
    )
    name = serializers.ReadOnlyField(  # в гугле CharField 
        source='ingredients.name'
    )

    class Meta:
        model = RecipeIngredients
        fields = (
            'id',
            'name',
            'amount',
            'measurement_unit',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=RecipeIngredients.objects.all(),
                fields=('recipe', 'ingredients')
            )
        ]


class RecipeListSerializer(serializers.ModelSerializer):    # тут все нормально
    """Сериализатор рецептов."""

    tags = TagSerializer(many=True, read_only=True)  # read_only=True точно надо?
    author = FoodgramUserSerializer(read_only=True)
    ingredients = RecipeIngredientsSerializer(
        many=True,
        source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

#     def get_ingredients(self, obj):
#         ingredients = RecipeIngredients.objects.filter(recipe=obj)
#         return IngredientsSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):  # тут не совпадает с гуглом
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favourites.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):  # тут не совпадает с гуглом
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
#         read_only_fields = (
#             'id',
#             'author',
#             'is_favorited',
#             'is_in_shopping_cart'
#         )


class RecipeSerializer(serializers.ModelSerializer):    # тут все нормально
    """Сериализатор рецепта."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    author = FoodgramUserSerializer(read_only=True)
    ingredients = IngredientsCreateSerializer(many=True)
    image = Base64ImageField(required=True)

    def validate_cooking_time(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше нуля'
            )
        return value

    def to_representation(self, instance):
        request = self.context.get('request')
        serializer = RecipeListSerializer(
            instance,
            context={'request': request}
        )
        return serializer.data

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        if not ingredients:
            raise serializers.ValidationError('нужен хотя бы один ингредиент')
        elif not tags:
            raise serializers.ValidationError('нужен хотя бы один тег')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        ingredients_list = [
            RecipeIngredients(
                recipe=recipe,
                ingredients=ingredient.get('id'),
                amount=ingredient.get('amount')
            )
            for ingredient in ingredients
        ]
        RecipeIngredients.objects.bulk_create(ingredients_list)
        return recipe

#    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        instance = super().update(instance, validated_data)
        if tags:
            instance.tags.set(tags)
        if ingredients:
            instance.ingredients.clear()
            ingredients_list = [
                RecipeIngredients(
                    recipe=instance,
                    ingredients=ingredient.get('id'),
                    amount=ingredient.get('amount')
                )
                for ingredient in ingredients
            ]
            RecipeIngredients.objects.bulk_create(ingredients_list)
        return instance

    def validate(self, data):  # в гугле другое
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError('Добавьте ингредиенты')
        ingredients_list = []
        for ingredient_item in ingredients:
            ingredient = ingredient_item['id']
            if ingredient in ingredients_list:
                raise serializers.ValidationError(
                    'Ингредиенты должны быть уникальными'
                )
            ingredients_list.append(ingredient)
        return data

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )


class FavouritesSerializer(serializers.ModelSerializer):
    """Сериализатор избранных рецептов."""

    class Meta:
        model = Favourites
        fields = '__all__'


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор списка покупок."""

    class Meta:
        model = ShoppingCart
        fields = '__all__'
