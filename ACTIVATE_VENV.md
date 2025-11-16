# Активация виртуального окружения

## Windows PowerShell

Для правильной активации виртуального окружения в PowerShell выполните:

```powershell
.venv\Scripts\Activate.ps1
```

Если вы получаете ошибку о политике выполнения, выполните:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Затем снова активируйте окружение:

```powershell
.venv\Scripts\Activate.ps1
```

## Windows Command Prompt (CMD)

```cmd
.venv\Scripts\activate.bat
```

## Альтернативный способ (без активации)

Вы можете запускать команды напрямую используя Python из виртуального окружения:

```powershell
.venv\Scripts\python.exe manage.py runserver
.venv\Scripts\python.exe manage.py migrate
.venv\Scripts\python.exe manage.py createsuperuser
```

## Проверка активации

После активации вы должны увидеть `(.venv)` в начале командной строки:

```
(.venv) C:\Users\merow\projects\infportal>
```

И при проверке Python должен указывать на виртуальное окружение:

```powershell
python -c "import sys; print(sys.executable)"
# Должно вывести: C:\Users\merow\projects\infportal\.venv\Scripts\python.exe
```

