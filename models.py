from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()

class Prompt(db.Model):
    __tablename__ = 'prompts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    target_model = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    
    # Relationship to access versions
    versions = db.relationship('PromptVersion', backref='prompt', cascade='all, delete-orphan', order_by='PromptVersion.version_number.desc')

class PromptVersion(db.Model):
    __tablename__ = 'prompt_versions'
    
    id = db.Column(db.Integer, primary_key=True)
    prompt_id = db.Column(db.Integer, db.ForeignKey('prompts.id', ondelete='CASCADE'), nullable=False)
    version_number = db.Column(db.Integer, nullable=True) # Let database trigger set this
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=True)
    ai_feedback = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

class PromptAuditLog(db.Model):
    __tablename__ = 'prompt_audit_log'
    
    id = db.Column(db.Integer, primary_key=True)
    prompt_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(50), nullable=False)
    happened_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
