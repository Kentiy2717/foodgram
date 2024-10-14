def get_purchased_in_file(buy):
    """Формирование списка покупок."""
    purchased = [
        'Список покупок:',
    ]
    for item in buy:
        name = item['ingredients__name']
        measurement_unit = item['ingredients__measurement_unit']
        amount = item['amount']
        purchased.append(
            f'{name}: {amount}, '
            f'{measurement_unit}'
        )
    return purchased
