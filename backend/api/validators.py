import re

from django.core.exceptions import ValidationError


def validate_username(username):
    """Валидатор юзернейма."""
    pattern = r'[a-zA-Z0-9@/./+/_/-]'
    banned_symbols = re.sub(pattern, '', username)
    if banned_symbols:
        raise ValidationError(
            f'Имя пользователя содержит недопустимые символы'
            f' - {banned_symbols}'
        )
    return username
