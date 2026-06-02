from google import genai
from config import Config

client = genai.Client(api_key=Config.GEMINI_API_KEY)


def analyze_prompt(content: str) -> str:
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=f"""Ти — експерт з написання AI-промптів.
Проаналізуй промпт і дай коротку відповідь у форматі:

**Якість:** (Відмінно / Добре / Задовільно / Потребує покращення)
**Сильні сторони:** (1-2 речення)
**Що покращити:** (1-2 конкретні поради)
**Покращена версія:** (переписаний промпт)

Промпт для аналізу:
{content}"""
        )
        return response.text
    except Exception as e:
        return f"Помилка аналізу: {str(e)}"


def compare_versions(old_content: str, new_content: str) -> str:
    try:
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=f"""Порівняй дві версії промпту і скажи що змінилось і чи стало краще.

**Стара версія:**
{old_content}

**Нова версія:**
{new_content}

Дай коротку відповідь: що змінилось, чи покращилось, що ще можна зробити."""
        )
        return response.text
    except Exception as e:
        return f"Помилка порівняння: {str(e)}"