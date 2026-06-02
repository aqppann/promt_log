from flask import Blueprint, render_template, redirect, url_for, flash
from models import db, Prompt, PromptVersion

versions_bp = Blueprint('versions', __name__)


# Список версій промпту
@versions_bp.route('/prompts/<int:prompt_id>/versions')
def list_versions(prompt_id):
    prompt = Prompt.query.get_or_404(prompt_id)
    versions = PromptVersion.query.filter_by(prompt_id=prompt_id)\
        .order_by(PromptVersion.version_number.desc()).all()
    return render_template('prompt_detail.html', prompt=prompt, versions=versions)


# Відновити конкретну версію
@versions_bp.route('/prompts/<int:prompt_id>/versions/<int:version_id>/restore', methods=['POST'])
def restore(prompt_id, version_id):
    prompt = Prompt.query.get_or_404(prompt_id)
    version = PromptVersion.query.get_or_404(version_id)

    prompt.content = version.content
    db.session.commit()

    flash(f'Відновлено версію #{version.version_number}', 'success')
    return redirect(url_for('prompts.detail', prompt_id=prompt_id))


# Видалити конкретну версію
@versions_bp.route('/prompts/<int:prompt_id>/versions/<int:version_id>/delete', methods=['POST'])
def delete_version(prompt_id, version_id):
    version = PromptVersion.query.get_or_404(version_id)
    db.session.delete(version)
    db.session.commit()

    flash('Версію видалено', 'info')
    return redirect(url_for('versions.list_versions', prompt_id=prompt_id))