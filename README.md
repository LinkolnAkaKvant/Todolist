# todolist - Планировщик задач #

Дипломная работа 12 патока "Python - разработчик" онлайн университета SkyPro

Thesis 12 molasses "Python - developer" online SkyPro University

----
## Особенности проекта | Project Features ##

- В проекте можно создавать доски, категрии задач и цели | In the project, you can create boards, task categories and goals
- В проекте доступна регистрация через VK | Registration through VK is available in the project
- Просматривать и создавать цели можно через telegram bot | View and create goals via telegram bot

____
## Stack: ##
Python 3.10

Django 4.1.7

PostgresQL

Docker

----

## Запуск проекта | Launch of the project ##

### 1 ###

#### Создание виртуального окружения | Creating a Virtual Environment: ####

- python -m venv venv

### 2 ###

#### Установка зависимостей | Setting dependencies: ###

 - pip install -r requirements.txt

### 3 ###

#### Скрытые переменные должны хранится в файле | Hidden variables must be stored in the file: ####

- .env

### 4 ###

#### Создание и применение миграций | Creating and implementing migration: ####

- python manage.py makemigrations 

- python manage.py migrate

### 5 ###

#### Создание и запуск контейнеров в Docker | Create and run containers in Docker: ####


- docker-compose up --build -d

### 6 ###

#### Команда для запуска проекта | Project start command: ####

- python manage.py runserver

  ### PS ###
  Посмотреть развернутый проект можно по ссылке http://158.160.84.117/auth
