# Информационный портал (Django)

Проект — минимальный рабочий каркас информационного портала на Django с использованием SQLite по умолчанию.

## Быстрый старт

1. Создайте виртуальное окружение и активируйте его:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```

2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

3. Выполните миграции и создайте суперпользователя:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. Запустите сервер:
   ```bash
   python manage.py runserver
   ```

5. Админ-панель: http://127.0.0.1:8000/admin/
   Сайт: http://127.0.0.1:8000/

## Использование PostgreSQL (опционально)
Установите PostgreSQL и настройте переменную окружения `DATABASE_URL` перед запуском:
```
export DATABASE_URL=postgres://USER:PASS@HOST:PORT/DBNAME
```
Убедитесь, что в виртуальном окружении установлен `psycopg2-binary` (pip install psycopg2-binary).

## Структура
- `infportal/` — Django project
- `portal/` — приложение с моделями Article, Category, Tag, Comment
- `templates/portal` — шаблоны
- `requirements.txt` — зависимости

## Что дальше можно добавить
- Авторизацию через социальные сети
- Рейтинг/оценки статей
- Панель модерации комментариев (на базе админки)
- RSS/ экспорт данных
