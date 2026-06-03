# Prompt Logger

Веб-додаток для зберігання, керування та AI-аналізу промптів.
Розробники щодня використовують AI-інструменти, але рідко зберігають та аналізують свої промпти — цей застосунок вирішує цю проблему.

## Технології

- Python 3.12 / Flask
- PostgreSQL + SQLAlchemy
- Groq AI (LLaMA 3.3)
- Jinja2 / Bootstrap 5

## Функціонал

- Створення, редагування, видалення промптів
- Автоматичне версіонування через PostgreSQL тригер
- AI-аналіз промпту через Groq API
- Історія версій з можливістю відновлення

---

## Реалізовані принципи для високого балу

### 1. Тригер (Trigger)

**Файл:** `database/init.sql`

При кожному оновленні поля `content` у таблиці `prompts` автоматично спрацьовує тригер `prompt_version_trigger`. Він викликає функцію `create_prompt_version()`, яка зберігає попередній текст у таблицю `prompt_versions` з автоматично обчисленим номером версії. Вся логіка виконується на рівні PostgreSQL — Flask не бере участі.

```sql
CREATE OR REPLACE TRIGGER prompt_version_trigger
BEFORE UPDATE ON prompts
FOR EACH ROW
EXECUTE FUNCTION create_prompt_version();
```

Перевірити наявність тригера:
```sql
SELECT trigger_name, event_manipulation
FROM information_schema.triggers
WHERE trigger_name = 'prompt_version_trigger';
```

---

### 2. Збережена процедура (Stored Function)

**Файл:** `database/init.sql` — оголошення, `routes/prompts.py` — виклик

Функція `get_best_version(p_id)` написана на PL/pgSQL і повертає найновішу збережену версію промпту за його `id`. Викликається з Flask через SQLAlchemy за допомогою `text()`.

```sql
CREATE OR REPLACE FUNCTION get_best_version(p_id INTEGER)
RETURNS TABLE(version_number INT, content TEXT, change_note VARCHAR, created_at TIMESTAMP)
AS $$ ... $$ LANGUAGE plpgsql;
```

Виклик з Flask:
```python
result = db.session.execute(
    text('SELECT * FROM get_best_version(:pid)'),
    {'pid': prompt_id}
).fetchone()
```

Перевірити наявність функцій у БД:
```sql
SELECT routine_name, routine_type
FROM information_schema.routines
WHERE routine_name IN ('create_prompt_version', 'get_best_version');
```

---

### 3. Транзакція (Transaction)

**Файл:** `routes/prompts.py` → функція `create_post()`

При створенні нового промпту в одній транзакції одночасно виконуються два записи — у таблицю `prompts` і у таблицю `prompt_versions` (перша версія). Використовується `db.session.flush()` для отримання `id` до фіксації. Якщо будь-яка операція завершується помилкою — викликається `db.session.rollback()` і жодних неповних даних у БД не залишається.

```python
try:
    db.session.add(prompt)
    db.session.flush()
    db.session.add(first_version)
    db.session.commit()
except Exception:
    db.session.rollback()
```

---

## Структура БД

```
prompts
├── id            SERIAL PRIMARY KEY
├── title         VARCHAR(255) NOT NULL
├── description   TEXT
├── content       TEXT NOT NULL
├── category      VARCHAR(100)
├── created_at    TIMESTAMP
└── updated_at    TIMESTAMP

prompt_versions
├── id             SERIAL PRIMARY KEY
├── prompt_id      INTEGER FK → prompts.id
├── version_number INTEGER NOT NULL
├── content        TEXT NOT NULL
├── change_note    VARCHAR(500)
├── ai_analysis    TEXT
└── created_at     TIMESTAMP
```

---

## Встановлення

1. Клонуй репозиторій:
```bash
git clone https://github.com/aqppann/promt_log.git
cd promt_log
```

2. Створи та активуй віртуальне середовище:
```bash
python -m venv venv
venv\Scripts\activate
```

3. Встанови залежності:
```bash
pip install -r requirements.txt
```

4. Створи `.env` файл у корені проєкту:
```env
SECRET_KEY=твій_секретний_ключ
DATABASE_URL=postgresql://postgres:пароль@localhost:5432/prompt_logger
GROQ_API_KEY=твій_groq_ключ
```

5. Створи таблиці та ініціалізуй БД:
```bash
python init_db.py
```

6. Запусти додаток:
```bash
python app.py
```

Відкрий браузер: `http://127.0.0.1:5000`

---

## Структура проєкту

```
promt_log/
├── database/
│   └── init.sql          # Тригер і збережена процедура
├── routes/
│   ├── prompts.py        # CRUD промптів + транзакція + виклик процедури
│   └── versions.py       # Керування версіями
├── services/
│   └── gemini.py         # Groq AI інтеграція
├── static/
│   └── style.css         # Стилі
├── templates/            # HTML шаблони (Jinja2)
├── models.py             # Моделі БД (SQLAlchemy)
├── app.py                # Фабрика Flask застосунку
├── config.py             # Конфігурація через .env
├── init_db.py            # Ініціалізація БД
└── requirements.txt      # Залежності
```