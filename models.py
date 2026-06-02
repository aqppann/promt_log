from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Prompt(db.Model):
    __tablename__ = 'prompts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Зв'язок з версіями
    versions = db.relationship('PromptVersion', backref='prompt', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Prompt {self.id}: {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'content': self.content,
            'category': self.category,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


class PromptVersion(db.Model):
    __tablename__ = 'prompt_versions'

    id = db.Column(db.Integer, primary_key=True)
    prompt_id = db.Column(db.Integer, db.ForeignKey('prompts.id'), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    change_note = db.Column(db.String(500), nullable=True)
    ai_analysis = db.Column(db.Text, nullable=True)  # результат Gemini-аналізу
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PromptVersion prompt={self.prompt_id} v{self.version_number}>'

    def to_dict(self):
        return {
            'id': self.id,
            'prompt_id': self.prompt_id,
            'version_number': self.version_number,
            'content': self.content,
            'change_note': self.change_note,
            'ai_analysis': self.ai_analysis,
            'created_at': self.created_at.isoformat(),
        }