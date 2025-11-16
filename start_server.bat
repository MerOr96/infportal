@echo off
REM Активация виртуального окружения и запуск сервера
call .venv\Scripts\activate.bat
python manage.py runserver
pause

