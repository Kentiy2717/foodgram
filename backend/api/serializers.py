import base64

from django.db import transaction
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

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


class Base64ImageField(serializers.ImageField):
    """Сериализатор для картинок."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class FoodgramUserSerializer(UserSerializer):
    """Сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=request.user, author=obj).exists()

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed',
            'avatar',
        ]
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


class SubscribtionsUserSerializer(FoodgramUserSerializer):
    """Сериализатор автора."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        read_only=True,
        source='recipes.count'
    )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        try:
            recipes_limit = int(recipes_limit)
            recipes = obj.recipes.all()[:recipes_limit]
        except (TypeError, ValueError):
            recipes = obj.recipes.all()
        return ShortRecipeSerializer(recipes, many=True).data

    class Meta(FoodgramUserSerializer.Meta):
        fields = FoodgramUserSerializer.Meta.fields + ['recipes',
                                                       'recipes_count']


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта. Короткий список данных."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class SubscribeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор подписки."""

    user = serializers.SlugRelatedField(
        slug_field='id',
        default=serializers.CurrentUserDefault(),
        read_only=True,
    )
    author = serializers.SlugRelatedField(
        slug_field='id',
        queryset=User.objects.all(),
    )

    def validate(self, data):
        if self.context['request'].user == data['author']:
            raise serializers.ValidationError(
                'Нельзя подписаться на себя.'
            )
        return data

    def to_representation(self, instance):
        return SubscribtionsUserSerializer(
            instance.author,
            context=self.context
        ).data

    class Meta:
        model = Subscribe
        fields = (
            'user',
            'author',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого пользователя.'
            )
        ]


class SubscribeListSerializer(serializers.ModelSerializer):
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


class SubscribeRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор подписки."""

    class Meta:
        model = Subscribe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тега."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'slug',
        )


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента."""

    class Meta:
        model = Ingredients
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class IngredientsCreateSerializer(serializers.ModelSerializer):
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


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов рецепта."""

    id = serializers.IntegerField(
        source='ingredients.id'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit'
    )
    name = serializers.ReadOnlyField(
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


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""

    tags = TagSerializer(many=True, read_only=True)
    author = FoodgramUserSerializer(read_only=True)
    ingredients = RecipeIngredientsSerializer(
        many=True,
        source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favourites.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
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


class RecipeSerializer(serializers.ModelSerializer):
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

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients', [])
        ingredients_id = [ingredient.get('id') for ingredient in ingredients]
        tags = self.initial_data.get('tags', [])
        if not ingredients:
            raise serializers.ValidationError('Добавьте ингредиенты')
        if len(ingredients_id) != len(set(ingredients_id)):
            raise serializers.ValidationError(
                'Ингредиенты должны быть уникальными'
            )
        if not tags:
            raise serializers.ValidationError('Добавьте теги')
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                'Теги должны быть уникальными'
            )
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
        fields = (
            'user',
            'recipe',
        )

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe,
            read_only=True
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор списка покупок."""

    class Meta:
        model = ShoppingCart
        fields = (
            'user',
            'recipe',
        )

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe,
            read_only=True
        ).data


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор аватара."""

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)

    def validate(self, data):
        if 'avatar' not in data:
            raise serializers.ValidationError(
                'Поле "avatar" обязательно для заполнения'
            )
        return data
