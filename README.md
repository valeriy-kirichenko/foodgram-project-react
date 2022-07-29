<!-- ![example workflow](https://github.com/valeriy-kirichenko/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg) -->
# Foodgram, «Продуктовый помощник» :hamburger:
Описание проекта
----------
На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

<!-- [Развернутый проект](http://51.250.17.23/api/v1/) -->
----------

# Установка
Системные требования
----------
* Python 3.9+
* Works on Linux, Windows, macOS, BSD

Стек технологий
----------
* Python 3.9
* Django 2.2
* Django Rest Framework
* Docker
* Docker-compose
* PostgreSQL
* Djoser

Запуск проекта
----------
Сперва установите [Docker](https://www.docker.com/get-started) и [Docker-compose](https://docs.docker.com/compose/install/), затем:
1. Клонируйте репозиторий, наберите в командной строке:
```bash
git clone 'git@github.com:valeriy-kirichenko/foodgram-project-react.git'
```
2. Переместитесь в папку /infra, создайте там файл .env и заполните его данными:
```bash
cd infra/
touch .env
nano .env
... # .env
SECRET_KEY= # Секретный ключ из settings.py
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER= # Придумайте пользователя
POSTGRES_PASSWORD= # Придумайте пароль
DB_HOST=db
DB_PORT=5432
... # сохраните (Ctl + x)
```
3. Не выходя из /infra выполните команду:
```bash
docker-compose up -d
```
4. Выводим список запущенных контейнеров:
```bash
docker ps # нас интересует контейнер web, скопируйте его 'CONTAINER ID'
```
5. Зайдите в командную строку контейнера, выполните команду:
```bash
docker exec -it <CONTAINER ID> /bin/bash
```
6. Находясь в командной строке контейнера выполняем миграции, собираем статику:
```bash
python manage.py migrate
python manage.py collectstatic --no-input
```
7. При желании можете наполнить БД тестовыми данными, выполните команду:
```bash
python manage.py load_data
```
----------
Автор:
----------
* **Кириченко Валерий Михайлович**
GitHub - [valeriy-kirichenko](https://github.com/valeriy-kirichenko)
----------
Документация к проекту с примерами запросов и ответов
----------
&ensp;&ensp;&ensp;&ensp;Документация для API [доступна по ссылке](http://localhost/api/docs/) после запуска приложения.