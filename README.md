# News Portal (+ Censorship Filter)

## Setup

1. Create venv and install deps:
```
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install django
```

2. Migrate:
```
.\.venv\Scripts\python.exe manage.py migrate
```

3. Run dev server:
```
.\.venv\Scripts\python.exe manage.py runserver
```

Open http://127.0.0.1:8000/news/

## Tests
```
.\.venv\Scripts\python.exe manage.py test
```

## Functionality
- List: /news/ — shows censored title and first 20 chars, date d.m.Y
- Detail: /news/<id>/ — shows censored title/content, date dd.mm.yyyy
- Censor filter: `news/templatetags/news_filters.py`, raises TypeError for non-strings


