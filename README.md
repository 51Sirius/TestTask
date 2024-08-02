# Тестовое задание

* [Текст задания](#tt)
* [Установка](#install)
* [Api](#api)

<a name="tt"></a>

## Текст задания

Написать docker compose, в котором работают:
web приложение, на FastApi. У приложения должно быть несколько ендпоинтов:

:white_check_mark: GET 'api/v1/messages/' показывает спосиок всех сообщений;

:white_check_mark: POST 'api/v1/message/' позволяет написать сообщение;

:white_check_mark: Веб сервер должен быть Nginx.

:white_check_mark: mongo как бд для сообщений.

:white_check_mark: Телеграм бот (aiogram3), который показывает сообщения и позволяет создать сообщение самому.

Будет плюсом:

:white_check_mark: Добавление кэширования при помощи Redis (кеш стирается, когда появляется новое сообщение)

:black_square_button: Развертывание на удалённом сервере и добавление ssl через certbot.

:white_check_mark: Реализовать код так, чтобы было видно, кто написал сообщение.

:white_check_mark: Добавление пагинации.

:white_check_mark: Проект залить на Github с подробно описанным Readme

<a name="install"></a>

## Установка

```
git clone https://github.com/51Sirius/TestTask.git
docker-compose up --build -d
```

В `bot.py` добавить токен бота.

Бот/ веб апп готов к использованию.

<a name="api"></a>

## Api

GET `http://web:8000/api/v1/messages`

```json
[
  {
    "_id": "ObjectId",
    "user": "username",
    "content": "content of message"
  }
]
```

POST `http://web:8000/api/v1/message`

```json
[
  {
    "user": "username",
    "content": "content of message"
  }
]
```


