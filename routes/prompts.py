from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Prompt, PromptVersion, PromptAuditLog
from sqlalchemy.sql import text

prompts_bp = Blueprint('prompts', __name__)

@prompts_bp.route('/')
def index():
    category_filter = request.args.get('category')
    model_filter = request.args.get('model')
    
    query = Prompt.query
    
    if category_filter:
        query = query.filter_by(category=category_filter)
    if model_filter:
        query = query.filter_by(target_model=model_filter)
        
    prompts = query.order_by(Prompt.created_at.desc()).all()
    
    # Enrich prompts with their best version and latest version details
    prompts_data = []
    for p in prompts:
        # Call the stored function to get the best version
        best_ver_row = db.session.execute(
            text("SELECT * FROM get_best_prompt_version(:p_id)"),
            {"p_id": p.id}
        ).fetchone()
        
        # Get the latest version
        latest_ver = PromptVersion.query.filter_by(prompt_id=p.id).order_by(PromptVersion.version_number.desc()).first()
        
        prompts_data.append({
            'prompt': p,
            'best_version': best_ver_row,
            'latest_version': latest_ver
        })
        
    # Get recent audit logs for the sidebar/activity log
    recent_logs = db.session.execute(
        text("""
            SELECT l.action, l.happened_at, p.title, p.id as prompt_id 
            FROM prompt_audit_log l
            JOIN prompts p ON l.prompt_id = p.id
            ORDER BY l.happened_at DESC
            LIMIT 10
        """)
    ).fetchall()
    
    return render_template(
        'index.html', 
        prompts_data=prompts_data, 
        recent_logs=recent_logs,
        category_filter=category_filter,
        model_filter=model_filter
    )

@prompts_bp.route('/prompts/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        target_model = request.form.get('target_model')
        content = request.form.get('content')
        rating = request.form.get('rating')
        
        if not title or not category or not target_model or not content:
            flash('All fields are required!', 'danger')
            return render_template('create.html')
            
        try:
            # Explicit Transaction
            prompt = Prompt(title=title, category=category, target_model=target_model)
            db.session.add(prompt)
            # Flush to get prompt.id
            db.session.flush()
            
            # The version_number is handled automatically by the DB trigger
            rating_val = int(rating) if rating else None
            version = PromptVersion(prompt_id=prompt.id, content=content, rating=rating_val)
            db.session.add(version)
            
            db.session.commit()
            flash('Prompt and its first version successfully created!', 'success')
            return redirect(url_for('prompts.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Transaction failed: {str(e)}. Rolled back changes.', 'danger')
            return render_template('create.html')
            
    return render_template('create.html')

@prompts_bp.route('/prompts/<int:id>')
def detail(id):
    prompt = Prompt.query.get_or_404(id)
    
    # Get all versions, newest first
    versions = PromptVersion.query.filter_by(prompt_id=id).order_by(PromptVersion.version_number.desc()).all()
    
    # Use stored procedure to get the best version
    best_ver_row = db.session.execute(
        text("SELECT * FROM get_best_prompt_version(:p_id)"),
        {"p_id": id}
    ).fetchone()
    
    # Get audit logs for this prompt
    audit_logs = db.session.execute(
        text("""
            SELECT action, happened_at 
            FROM prompt_audit_log 
            WHERE prompt_id = :p_id 
            ORDER BY happened_at DESC
        """),
        {"p_id": id}
    ).fetchall()
    
    return render_template(
        'prompt_detail.html', 
        prompt=prompt, 
        versions=versions, 
        best_version=best_ver_row,
        audit_logs=audit_logs
    )

@prompts_bp.route('/prompts/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    prompt = Prompt.query.get_or_404(id)
    # Get the latest version to populate current content
    latest_version = PromptVersion.query.filter_by(prompt_id=id).order_by(PromptVersion.version_number.desc()).first()
    
    if request.method == 'POST':
        content = request.form.get('content')
        rating = request.form.get('rating')
        
        if not content:
            flash('Content is required for the new version!', 'danger')
            return render_template('edit.html', prompt=prompt, latest_version=latest_version)
            
        try:
            rating_val = int(rating) if rating else None
            # Creating a new version rather than editing
            new_version = PromptVersion(prompt_id=id, content=content, rating=rating_val)
            db.session.add(new_version)
            db.session.commit()
            
            flash('New prompt version successfully saved!', 'success')
            return redirect(url_for('prompts.detail', id=id))
        except Exception as e:
            db.session.rollback()
            flash(f'Failed to add version: {str(e)}', 'danger')
            return render_template('edit.html', prompt=prompt, latest_version=latest_version)
            
    return render_template('edit.html', prompt=prompt, latest_version=latest_version)

@prompts_bp.route('/prompts/<int:id>/delete', methods=['POST'])
def delete(id):
    prompt = Prompt.query.get_or_404(id)
    try:
        db.session.delete(prompt)
        db.session.commit()
        flash('Prompt deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting prompt: {str(e)}', 'danger')
    return redirect(url_for('prompts.index'))
