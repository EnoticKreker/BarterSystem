### УСТАНОВКА
1. Устаноить виртуальное окружение командой:
    (windows)
   ```bash
    python -m venv venv
   ```

    (linux/macOS)
   ```bash
   python3 -m venv venv
   ```

2. Активировать виртуальное окружение командой:
    (windows)
   ```bash
   .\venv\Scripts\activate
   ```
   
    (linux/macOS)
   ```bash
   source venv/bin/activate
   ```

3. Скопировать проект с помощью git clone в папку с venv.
   ```bash
   git clone https://github.com/EnoticKreker/BarterSystem.git
   ```

4. Перейти в папку BarterSystem и запустить команду для установки зависимостей
   ```bash
   pip install -r requirements.txt
   ```

### ВЫПОЛНЕНИЕ МИГРАЦИЙ И СОЗДАНИЯ ПОЛЬЗОВАТЕЛЯ

1. Запустить команды для базы данных описсывающие какие измененеия нужно внести в структуру таблиц (models):
    ```bash
    python manage.py makemigrations
    python manage.py makemigrations barter
    ```

2. Запустить команду для применения изменений в БД: 
    ```bash
    python manage.py migrate
    ```
    
3. Создать пользователя с правами администратора. Указать его наименование, почту и задать пароль:
   ```bash
   python manage.py createsuperuser
    ```
   
4. Создать пользователя с обычными правами (default user).
    1. Можно через встроенную панель администратора после запуска:
       Запустить cсервер командой:
           (windows)
       ```bash
       python manage.py runserver
       ```
       (linux/macOS)
       ```bash
       python3 manage.py runserver
       ```
        - Перейти по ссылке http://127.0.0.1:8000/admin/login/?next=/admin/
        - Авторизовать с помощью учётной записи с правами администратора. (Пункт 3)
        - Перейти в пользователи (http://127.0.0.1:8000/admin/auth/user/) и добавить пользователя (http://127.0.0.1:8000/admin/auth/user/add/).
    3. Можно создать с помощью командной строки.
        - Запустить в командной строке:
              (windows)
          ```bash
          python manage.py shell
          ```
          (linux/macOS)
          ```bash
          python3 manage.py shell
          ```
        - Вставить следующие команды (Можно построчно или целиком):
            ```
            from django.contrib.auth.models import User
            user = User.objects.create_user(username='testuser', password='12345')
            user.email = 'test@example.com'
            user.save()
            ```

### ЗАПУСК СЕРВЕРА

1. Запускаем сервер командой:
    ```bash
    python manage.py runserver
    ```

2. Перейти в бразуер и в поиской строке указать 
    - http://127.0.0.1:8000

### ТЕСТИРОВАНИЕ
1. Нужно из корневой папки проекта (где лежит файл manage.py) запустить команду:
    ```bash
    pytest
    ```
