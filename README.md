# api_yamdb

### Как запустить проект:
1. Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/AlexanderKuryatnikov/api_yamdb.git
```

```
cd api_yamdb
```

2. Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

```
source venv/script/activate
```

3. Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

4. Выполнить миграции:

```
python manage.py migrate
```

5. Загрузить данные из csv:

```
python manage.py loadcsv
```

7. Запустить проект:

```
python manage.py runserver
```

### Документация по api:
Документация доступна после запуска проекта по ссылке http://127.0.0.1:8000/redoc/

### Авторы проекта:
------
* Александр Курятников
* Алексей Коломейцев
* Артем Лайченков