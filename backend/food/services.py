import random

from food.constants import (
    CHARACTERS,
    TOKEN_LENGTH,
)


def generate_short_url(self):
    """Генерация коротной ссылки."""
    if not self.short_url:
        while True:
            self.short_url = ''.join(
                random.choices(
                    CHARACTERS,
                    k=TOKEN_LENGTH
                )
            )
            if not self.__class__.objects.filter(
                short_url=self.short_url
            ).exists():
                break
