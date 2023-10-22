# *FOODGRAM*
Foodgram - "продуктовый помощник". Данный проект является диполмным. На сайте можно создавать рецепты, подписываться на рецепты других пользователей, добавлять рецепты в список «Избранное», также скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

# Запуск проекта локально
## Клонируйте репозиторий:
```
git clone git@github.com:koan1010101/foodgram-project-react.git
```
## Установите и активируйте виртуальное окружение:

для MacOS
```
python3 -m venv venv
```
для Windows
```
python -m venv venv
source venv/bin/activate
source venv/Scripts/activate
```
## Установите зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
## Примените миграции:
```
python manage.py migrate
```
## В папке с файлом manage.py выполните команду для запуска локально:
```
python manage.py runserver
```
## Локально Документация доступна по адресу:
```
http://127.0.0.1/api/docs/
```
# Запус проекта локально в контейнерах

## Клонировать репозиторий и перейти в него в командной строке:
```
git@github.com:koan1010101/foodgram-project-react.git cd foodgram-project-react
```
## Запустить docker-compose:
```
docker-compose up
```
## После окончания сборки контейнеров выполнить миграции:
```
docker-compose exec web python manage.py migrate
```
## Создать суперпользователя:
```
docker-compose exec web python manage.py createsuperuser
```
## Собрать статику:
```
docker-compose exec web python manage.py collectstatic --no-input
```
## Проект доступен по ссылке:
```
http://localhost/
```
# Запус проекта на сервере:

## Добавить в Secrets на Github следующие данные:
```
DB_ENGINE=django.db.backends.postgresql # указать, что проект работает с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД
DB_HOST=db # название сервиса БД (контейнера) 
DB_PORT=5432 # порт для подключения к БД
DOCKER_PASSWORD= # Пароль от аккаунта на DockerHub
DOCKER_USERNAME= # Username в аккаунте на DockerHub
HOST= # IP удалённого сервера
USER= # Логин на удалённом сервере
SSH_KEY= # SSH-key компьютера, с которого будет происходить подключение к удалённому серверу
PASSPHRASE= #Если для ssh используется фраза-пароль
TELEGRAM_TO= #ID пользователя в Telegram
TELEGRAM_TOKEN= #ID бота в Telegram
```
## Выполнить команды:
```
git add .
git commit -m "Коммит"
git push
```
## После этого будут запущены процессы workflow:

- Проверка кода на соответствие стандарту PEP8 (с помощью пакета flake8) и запуск pytest
- CI/CD
- Отправка уведомления в Telegram о том, что процесс деплоя успешно завершился

# В API доступны следующие эндпоинты:
- **/api/users/ Get-запрос** – получение списка пользователей. POST-запрос – регистрация нового пользователя. Доступно без токена.

- **/api/users/{id} GET-запрос** – персональная страница пользователя с указанным id (доступно без токена).

- **/api/users/me/ GET-запрос** – страница текущего пользователя. PATCH-запрос – редактирование собственной страницы. Доступно авторизированным пользователям.

- **/api/users/set_password** POST-запрос – изменение собственного пароля. Доступно авторизированным пользователям.

- **/api/auth/token/login/** POST-запрос – получение токена. Используется для авторизации по емейлу и паролю, чтобы далее использовать токен при запросах.

- **/api/auth/token/logout/** POST-запрос – удаление токена.

- **/api/tags/** GET-запрос — получение списка всех тегов. Доступно без токена.

- **/api/tags/{id**} GET-запрос — получение информации о теге о его id. Доступно без токена.

- **/api/ingredients/** GET-запрос – получение списка всех ингредиентов. Подключён поиск по частичному вхождению в начале названия ингредиента. Доступно без токена.

- **/api/ingredients/{id}/** GET-запрос — получение информации об ингредиенте по его id. Доступно без токена.

- **/api/recipes/** GET-запрос – получение списка всех рецептов. Возможен поиск рецептов по тегам и по id автора (доступно без токена). POST-запрос – добавление нового рецепта (доступно для авторизированных пользователей).

- **/api/recipes/?is_favorited=1** GET-запрос – получение списка всех рецептов, добавленных в избранное. Доступно для авторизированных пользователей.

- **/api/recipes/is_in_shopping_cart=1** GET-запрос – получение списка всех рецептов, добавленных в список покупок. Доступно для авторизированных пользователей.

- **/api/recipes/{id}/** GET-запрос – получение информации о рецепте по его id (доступно без токена). PATCH-запрос – изменение собственного рецепта (доступно для автора рецепта). DELETE-запрос – удаление собственного рецепта (доступно для автора рецепта).

- **/api/recipes/{id}/favorite/** POST-запрос – добавление нового рецепта в избранное. DELETE-запрос – удаление рецепта из избранного. Доступно для авторизированных пользователей.

- **/api/recipes/{id}/shopping_cart/** POST-запрос – добавление нового рецепта в список покупок. DELETE-запрос – удаление рецепта из списка покупок. Доступно для авторизированных пользователей.

- **/api/recipes/download_shopping_cart/** GET-запрос – получение текстового файла со списком покупок. Доступно для авторизированных пользователей.

- **/api/users/{id}/subscribe/** GET-запрос – подписка на пользователя с указанным id. POST-запрос – отписка от пользователя с указанным id. Доступно для авторизированных пользователей

- **/api/users/subscriptions/** GET-запрос – получение списка всех пользователей, на которых подписан текущий пользователь Доступно для авторизированных пользователей.

# Автор проекта
**Никулин Владимир**

![Alt-текст](https://forum.clientmod.ru/attachments/223/)

