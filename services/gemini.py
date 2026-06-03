from groq import Groq
from config import Config

client = Groq(api_key=Config.GROQ_API_KEY)


def analyze_prompt(content: str) -> str:
    try:
        response = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=[
                {
                    "role": "user",
                    "content": f"""Ти — експерт з написання AI-промптів.
Проаналізуй промпт і дай коротку відповідь у форматі:

**Якість:** (Відмінно / Добре / Задовільно / Потребує покращення)
**Сильні сторони:** (1-2 речення)
**Що покращити:** (1-2 конкретні поради)
**Покращена версія:** (переписаний промпт)

Промпт для аналізу:
{content}"""
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Помилка аналізу: {str(e)}"


def compare_versions(old_content: str, new_content: str) -> str:
    try:
        response = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=[
                {
                    "role": "user",
                    "content": f"""Порівняй дві версії промпту і скажи що змінилось і чи стало краще.

**Стара версія:**
{old_content}

**Нова версія:**
{new_content}

Дай коротку відповідь: що змінилось, чи покращилось, що ще можна зробити."""
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Помилка порівняння: {str(e)}"