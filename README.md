### Проект "Фудграм"
Дипломный проект в рамках обучения на курсе "Python разработчик буткемп" Яндекс Практикума. Разработка бэкенд в виде REST API для веб-приложения и настройка автоматической публикации этого веб-приложения на виртуальном удалённом сервере.

![example workflow](https://github.com/Kentiy2717/foodgram/actions/workflows/main.yml/badge.svg)

### Технологии

Python, Django, Django Rest Framework, REST API, Docker, Nginx, GitHub, GitHub Actions

### Команда проекта

Исполнитель:

Иннокентий Мотрий (https://github.com/Kentiy2717).

Наставники:

Ритис Бараускас, Николай Минякин. 

Ревьюер:

Евгений Салахутдинов.

2024г.

### Как запустить проект

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Kentiy2717/foodgram.git
```

```
cd foodgram
```

Cоздать и активировать виртуальное окружение:

* Если у вас Linux/macOS

    ```
    python3 -m venv env
    source env/bin/activate
    ```

* Если у вас Windows

    ```
    python -m venv env
    source env/scripts/activate
    ```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

* Запустить проект локально через Docker:

```
bash start-local-docker.sh

Проект будет доступен по адресу http://localhost:8080/
```

* Удаленно проект "Foodgram" - доступен по адресу:

```
 https://sherrycask.zapto.org/
```

### Документация

Документация API и примеры запросов доступны по адресу https://sherrycask.zapto.org/api/docs/

### Пример запроса

Список рецептов.

Страница доступна всем пользователям. Доступна фильтрация по избранному, автору, списку покупок и тегам.

При переходе в браузере по адресу https://sherrycask.zapto.org/api/recipes/

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

### Документация локально

Находясь в папке infra, выполните команду docker-compose up. При выполнении этой команды контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.

По адресу http://localhost изучите фронтенд веб-приложения, а по адресу http://localhost/api/docs/ — спецификацию API.
