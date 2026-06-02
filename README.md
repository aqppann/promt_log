# Prompt Logger

Веб-додаток для зберігання, керування та AI-аналізу промптів.

## Технології

- Python 3.12 / Flask
- PostgreSQL + SQLAlchemy
- Gemini AI (google-genai)
- Jinja2 templates

## Функціонал

- Створення, редагування, видалення промптів
- Автоматичне збереження версій через PostgreSQL тригер
- AI-аналіз промпту через Gemini
- Історія версій з можливістю відновлення

## Встановлення

1. Клонуй репозиторій:

```bash
git clone https://github.com/твій_юзернейм/promt_log.git
cd promt_log
```

2. Створи та активуй venv:

```bash
python -m venv venv
venv\Scripts\activate
```

3. Встанови залежності:

```bash
pip install -r requirements.txt
```

4. Створи `.env` файл:

```
SECRET_KEY=твій_секретний_ключ
DATABASE_URL=postgresql://user:password@localhost:5432/prompt_logger
GEMINI_API_KEY=твій_gemini_ключ
```

5. Створи БД та таблиці:

```bash
python init_db.py
```

6. Запусти додаток:

```bash
python app.py
```

Відкрий браузер: `http://127.0.0.1:5000`

## Структура проєкту

```
promt_log/
├── database/
│   └── init.sql          # Тригер і збережена процедура
├── routes/
│   ├── prompts.py        # CRUD промптів
│   └── versions.py       # Керування версіями
├── services/
│   └── gemini.py         # Gemini AI інтеграція
├── static/
│   └── style.css         # Стилі
├── templates/            # HTML шаблони
├── models.py             # Моделі БД
├── app.py                # Ініціалізація Flask
├── config.py             # Конфігурація
└── init_db.py            # Ініціалізація БД
```