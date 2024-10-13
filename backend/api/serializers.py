from drf_extra_fields.fields import Base64ImageField

from django.db import transaction
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator


from food.constants import MAX_AMOUNT_VALUE, MIN_AMOUNT_VALUE
from food.services import ingredient_list
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


class FoodgramUserSerializer(UserSerializer):
    """Сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta(UserSerializer.Meta):
        model = User
        fields = UserSerializer.Meta.fields + ('is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        request = self.context['request']
        return (request and request.user.is_authenticated
                and obj.subscriptions_on_author.filter(
                    user=request.user
                ).exists())


class SubscribtionsUserSerializer(FoodgramUserSerializer):
    """Сериализатор автора."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        read_only=True,
        default=0
    )

    class Meta(FoodgramUserSerializer.Meta):
        fields = FoodgramUserSerializer.Meta.fields + ('recipes',
                                                       'recipes_count')

    def get_recipes(self, obj):
        request = self.context['request']
        recipes_limit = request.GET.get('recipes_limit')
        try:
            recipes_limit = int(recipes_limit)
        except TypeError:
            recipes_limit = None
        recipes = obj.recipes.all()[:recipes_limit]
        return ShortRecipeSerializer(
            recipes,
            many=True,
            context=self.context
        ).data


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
    amount = serializers.IntegerField(
        min_value=MIN_AMOUNT_VALUE,
        max_value=MAX_AMOUNT_VALUE
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

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and obj.favourites.filter(user=request.user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and obj.shoppingcart.filter(user=request.user).exists()
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

    def to_representation(self, instance):
        return RecipeListSerializer(
            instance,
            context=self.context
        ).data

    def validate_ingredients(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                'Добавьте хотя бы один ингредиент.'
            )
        return data

    def validate_tags(self, data):
        tags = self.initial_data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                'Выберите хотя бы один тег.'
            )
        return data

    @transaction.atomic
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        ingredient_list(self, recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        instance.tags.set(tags)
        instance.ingredients.clear()
        ingredient_list(self, instance, ingredients)
        instance = super().update(instance, validated_data)
        return instance

    def validate(self, data):
        ingredients = data.get('ingredients', [])
        ingredients_id = [ingredient.get('id') for ingredient in ingredients]
        tags = data.get('tags', [])
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


class BaseSerializer(serializers.ModelSerializer):
    class Meta:
        abstract = True

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe,
            read_only=True
        ).data

    def validate(self, data):
        """Проверка на уникальность пары рецепта и пользователя."""
        user = data.get('user')
        recipe = data.get('recipe')
        if self.Meta.model.objects.filter(recipe=recipe, user=user).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в {self.Meta.model._meta.verbose_name}'
            )
        return data


class FavouritesSerializer(BaseSerializer):
    """Сериализатор избранных рецептов."""

    class Meta:
        model = Favourites
        fields = (
            'user',
            'recipe',
        )


class ShoppingCartSerializer(BaseSerializer):
    """Сериализатор списка покупок."""

    class Meta:
        model = ShoppingCart
        fields = (
            'user',
            'recipe',
        )


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
