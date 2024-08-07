from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from food.models import User
from .validators import validate_username
from users.constants import NAME_MAX_LENGTH, EMAIL_MAX_LENGTH


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""

    class Meta:
        model = User
        fields = (
            'username',
            'id',
            'email',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        max_length=EMAIL_MAX_LENGTH,
    )
    username = serializers.CharField(
        required=True,
        max_length=NAME_MAX_LENGTH,
    )
    first_name = serializers.CharField(
        required=True,
        max_length=NAME_MAX_LENGTH,
    )
    last_name = serializers.CharField(
        required=True,
        max_length=NAME_MAX_LENGTH,
    )
    password = serializers.CharField(
        required=True,
        max_length=NAME_MAX_LENGTH,
    )

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
        email = validated_data.get('email')
        username = validated_data.get('username')
        first_name = validated_data.get('first_name')
        last_name = validated_data.get('last_name')
        password = validated_data.get('password')
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password
        )
        user.save()
        return user