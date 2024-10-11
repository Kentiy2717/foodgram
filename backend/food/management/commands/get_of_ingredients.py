import csv

from django.core.management.base import BaseCommand

from food.models import Ingredients


class Command(BaseCommand):
    help = 'Загрузка данных из csv файла в модель Ingredients'
    stealth_options = True

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str, help='Путь к файлу')

    def handle(self, *args, **options):
        '''
        Загрузка данных из csv файла в модель Ingredients.
        При помощи метода bulk_create.
        со страховкой открытия файла.'''
        file_path = options['path'] + 'ingredients.csv'
        with open(file_path, encoding='utf-8') as file:
            ingredients = list(csv.reader(file))
            Ingredients.objects.bulk_create([
                Ingredients(name=ingredient[0], measurement_unit=ingredient[1])
                for ingredient in ingredients
            ], ignore_conflicts=False)
