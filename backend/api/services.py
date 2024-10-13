from food.models import Ingredients


def get_purchased_in_file(buy):
    """Формирование списка покупок."""
    purchased = [
        'Список покупок:',
    ]
    for item in buy:
        ingredient = Ingredients.objects.get(pk=item["ingredients"])
        amount = item["amount"]
        purchased.append(
            f"{ingredient.name}: {amount}, "
            f"{ingredient.measurement_unit}"
        )
    return purchased
