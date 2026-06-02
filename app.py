import os
from flask import Flask
from config import Config
from models import db
from routes.prompts import prompts_bp
from routes.versions import versions_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize DB
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(prompts_bp)
    app.register_blueprint(versions_bp)
    
    # Custom filters
    @app.template_filter('datetimeformat')
    def datetimeformat(value):
        if not value:
            return ""
        return value.strftime('%d.%m.%Y %H:%M')
        
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
