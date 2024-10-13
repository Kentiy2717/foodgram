import csv

from django.core.management.base import BaseCommand

from food.models import Ingredients


class Command(BaseCommand):
    help = 'Загрузка данных из csv файла в модель Ingredients'
    stealth_options = True

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str, help='Путь к файлу')

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Загрузка данных...'))
        file_path = options['path'] + 'ingredients.csv'
        try:
            with open(file_path, encoding='utf-8') as file:
                ingredients = list(csv.reader(file))
                Ingredients.objects.bulk_create([
                    Ingredients(
                        name=ingredient[0],
                        measurement_unit=ingredient[1]
                    )
                    for ingredient in ingredients
                ], ignore_conflicts=True)
                self.stdout.write(self.style.SUCCESS('Данные загружены'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('Файл не существует'))
            return
