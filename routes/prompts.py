from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Prompt

prompts_bp = Blueprint('prompts', __name__)


# Список всіх промптів
@prompts_bp.route('/')
def index():
    prompts = Prompt.query.order_by(Prompt.created_at.desc()).all()
    return render_template('index.html', prompts=prompts)


# Деталі промпту
@prompts_bp.route('/prompts/<int:prompt_id>')
def detail(prompt_id):
    prompt = Prompt.query.get_or_404(prompt_id)
    return render_template('prompt_detail.html', prompt=prompt)


# Створення промпту — форма
@prompts_bp.route('/prompts/create', methods=['GET'])
def create():
    return render_template('create.html')


# Створення промпту — збереження
@prompts_bp.route('/prompts/create', methods=['POST'])
def create_post():
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    description = request.form.get('description', '').strip()
    category = request.form.get('category', '').strip()

    if not title or not content:
        flash('Назва та зміст обовʼязкові', 'error')
        return redirect(url_for('prompts.create'))

    prompt = Prompt(
        title=title,
        content=content,
        description=description,
        category=category
    )
    db.session.add(prompt)
    db.session.commit()

    flash('Промпт створено!', 'success')
    return redirect(url_for('prompts.detail', prompt_id=prompt.id))


# Редагування промпту — форма
@prompts_bp.route('/prompts/<int:prompt_id>/edit', methods=['GET'])
def edit(prompt_id):
    prompt = Prompt.query.get_or_404(prompt_id)
    return render_template('edit.html', prompt=prompt)


# Редагування промпту — збереження
@prompts_bp.route('/prompts/<int:prompt_id>/edit', methods=['POST'])
def edit_post(prompt_id):
    prompt = Prompt.query.get_or_404(prompt_id)

    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    description = request.form.get('description', '').strip()
    category = request.form.get('category', '').strip()

    if not title or not content:
        flash('Назва та зміст обовʼязкові', 'error')
        return redirect(url_for('prompts.edit', prompt_id=prompt_id))

    prompt.title = title
    prompt.content = content  # ← тут спрацює тригер PostgreSQL
    prompt.description = description
    prompt.category = category

    db.session.commit()

    flash('Промпт оновлено!', 'success')
    return redirect(url_for('prompts.detail', prompt_id=prompt.id))


# Видалення промпту
@prompts_bp.route('/prompts/<int:prompt_id>/delete', methods=['POST'])
def delete(prompt_id):
    prompt = Prompt.query.get_or_404(prompt_id)
    db.session.delete(prompt)
    db.session.commit()

    flash('Промпт видалено', 'info')
    return redirect(url_for('prompts.index'))