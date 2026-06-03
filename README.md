# Prompt Logger

Веб-додаток для зберігання, керування та AI-аналізу промптів. Розробники щодня використовують AI-інструменти, але рідко зберігають та аналізують свої промпти — цей застосунок вирішує цю проблему.

## Технології

- Python 3.12 / Flask
- PostgreSQL + SQLAlchemy
- Gemini AI (google-genai)
- Jinja2 templates
- Bootstrap 5

## Функціонал

- Створення, редагування, видалення промптів
- Автоматичне збереження версій через PostgreSQL тригер
- AI-аналіз промпту через Gemini
- Історія версій з можливістю відновлення

## Реалізовані принципи для високого балу

### 1. Тригер (Trigger)
При оновленні поля `content` у таблиці `prompts` автоматично спрацьовує тригер `prompt_version_trigger`. Він зберігає попередню версію тексту в таблицю `prompt_versions` з автоматичним номером версії. Файл: `database/init.sql`

### 2. Збережена процедура (Stored Function)
Функція `get_best_version(prompt_id)` у PostgreSQL повертає найновішу збережену версію для вказаного промпту. Викликається з Flask через SQLAlchemy за допомогою `text()`. Файл: `database/init.sql`, виклик у `routes/prompts.py`

### 3. Транзакція (Transaction)
При створенні нового промпту в одній транзакції одночасно створюється запис у таблиці `prompts` і перша версія в `prompt_versions`. Якщо будь-яка з операцій завершується помилкою — виконується `rollback`, і жодних неповних даних у БД не залишається. Файл: `routes/prompts.py` → функція `create_post()`

## Структура БД
prompts — id, title, description, content, category, created_at, updated_at
prompt_versions — id, prompt_id (FK), version_number, content, change_note, ai_analysis, created_at

## Встановлення

1. Клонуй репозиторій:
```bash
git clone https://github.com/aqppann/promt_log.git
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
SECRET_KEY=твій_секретний_ключ
DATABASE_URL=postgresql://postgres:пароль@localhost:5432/prompt_logger
GEMINI_API_KEY=твій_gemini_ключ
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
promt_log/
├── database/
│   └── init.sql          # Тригер і збережена процедура
├── routes/
│   ├── prompts.py        # CRUD промптів + транзакція
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