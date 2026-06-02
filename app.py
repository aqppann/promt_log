from flask import Flask
from config import Config
from models import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ініціалізація БД
    db.init_app(app)

    # Реєстрація blueprints
    from routes.prompts import prompts_bp
    from routes.versions import versions_bp

    app.register_blueprint(prompts_bp)
    app.register_blueprint(versions_bp)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)