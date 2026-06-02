from datetime import timedelta
from flask import Flask
from config import Config
from models import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    @app.template_filter('ua_time')
    def ua_time_filter(dt):
        if dt is None:
            return ''
        return (dt + timedelta(hours=3)).strftime('%d.%m.%Y %H:%M')

    from routes.prompts import prompts_bp
    from routes.versions import versions_bp

    app.register_blueprint(prompts_bp)
    app.register_blueprint(versions_bp)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)