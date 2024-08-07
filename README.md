Находясь в папке infra, выполните команду docker-compose up. При выполнении этой команды контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.

По адресу http://localhost изучите фронтенд веб-приложения, а по адресу http://localhost/api/docs/ — спецификацию API.

### Проект "Фудграм"
Дипломный проект в рамках обучения на курсе "Python разработчик буткемп" Яндекс Практикума. Разработка бэкенд приложения и настройка автодеплоя на сервер в Docker.

![example workflow](https://github.com/Kentiy2717/foodgram/actions/workflows/main.yml/badge.svg)

Август 2024.

### Технологии

Python, Django, Django Rest Framework, Pytest, Flake8, Docker, CI/CD

### Команда проекта

Исполнитель:

Иннокентий Мотрий (https://github.com/Kentiy2717).

Наставники:

Ритис Бараускас, Николай Минякин. 

Ревьюер:

Евгений Салахутдинов.

### Как запустить проект

Проект "Foodgram" - доступен по адресу https://sherrycask.zapto.org/

### Документация

Документация API и примеры запросов доступны по адресу https://sherrycask.zapto.org/api/docs/

### Пример запроса

Список рецептов.

Страница доступна всем пользователям. Доступна фильтрация по избранному, автору, списку покупок и тегам.

При переходе в браузере по адресу http://sherrycask.jumpingcrab.com/api/recipes/

пользователь получит ответ следующего формата:

```
{
    "count": 123,
    "next": "http://foodgram.example.org/api/recipes/?page=4",
    "previous": "http://foodgram.example.org/api/recipes/?page=2",
    "results": [
        + { ... }
    ]
}
```
