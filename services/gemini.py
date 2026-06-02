import google.generativeai as genai
from config import Config

genai.configure(api_key=Config.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')


def analyze_prompt(content: str) -> str:
    """Аналізує промпт через Gemini і повертає рекомендації."""
    try:
        system = """Ти — експерт з написання AI-промптів. 
Проаналізуй промпт і дай коротку відповідь у форматі:

**Якість:** (Відмінно / Добре / Задовільно / Потребує покращення)
**Сильні сторони:** (1-2 речення)
**Що покращити:** (1-2 конкретні поради)
**Покращена версія:** (переписаний промпт)
"""
        response = model.generate_content(f"{system}\n\nПромпт для аналізу:\n{content}")
        return response.text

    except Exception as e:
        return f"Помилка аналізу: {str(e)}"


def compare_versions(old_content: str, new_content: str) -> str:
    """Порівнює дві версії промпту."""
    try:
        prompt = f"""Порівняй дві версії промпту і скажи що змінилось і чи стало краще.

**Стара версія:**
{old_content}

**Нова версія:**
{new_content}

Дай коротку відповідь: що змінилось, чи покращилось, що ще можна зробити.
"""
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"Помилка порівняння: {str(e)}"