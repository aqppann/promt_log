from app import create_app
from models import db
import os

app = create_app()

with app.app_context():
    # Створює всі таблиці
    db.create_all()
    print("✅ Таблиці створено")

    # Виконує тригер і процедуру з init.sql
    sql_path = os.path.join(os.path.dirname(__file__), 'database', 'init.sql')
    with open(sql_path, 'r') as f:
        sql = f.read()

    db.session.execute(db.text(sql))
    db.session.commit()
    print("✅ Тригер і процедура створені")