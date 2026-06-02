import os
import google.generativeai as genai
from flask import Blueprint, request, redirect, url_for, flash, jsonify
from models import db, PromptVersion

versions_bp = Blueprint('versions', __name__)

@versions_bp.route('/versions/<int:id>/rate', methods=['POST'])
def rate(id):
    version = PromptVersion.query.get_or_404(id)
    rating = request.form.get('rating')
    
    if not rating:
        flash('Rating is required!', 'warning')
        return redirect(url_for('prompts.detail', id=version.prompt_id))
        
    try:
        rating_val = int(rating)
        if rating_val < 1 or rating_val > 5:
            flash('Rating must be between 1 and 5 stars!', 'danger')
        else:
            version.rating = rating_val
            db.session.commit() # Trigger will run and insert 'rated' action in audit log
            flash(f'Successfully rated Version {version.version_number} with {rating_val} stars!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to update rating: {str(e)}', 'danger')
        
    return redirect(url_for('prompts.detail', id=version.prompt_id))

@versions_bp.route('/versions/<int:id>/analyze', methods=['POST'])
def analyze(id):
    version = PromptVersion.query.get_or_404(id)
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        flash('Gemini API key is not set in the configuration!', 'danger')
        return redirect(url_for('prompts.detail', id=version.prompt_id))
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3.5-flash')
        
        system_instruction = (
            "You are an AI prompt engineering auditor. Your job is to analyze prompt structure, clarity, "
            "context, and constraints, then provide structured feedback. Output ONLY clean HTML content. "
            "Do not wrap it in markdown codeblocks (```html) or write any surrounding comments. Use "
            "semantic tags: <h4>, <ul>, <li>, <p>, <strong>, and a styled <blockquote> for the rewritten prompt."
        )
        
        prompt_analysis_request = f"""
        Analyze the following prompt and evaluate it based on clarity, specificity, instructions, and target audience.
        Provide suggestions to make it better.
        
        ---
        PROMPT TO ANALYZE:
        {version.content}
        ---
        
        Output format:
        <h4>💡 Strengths</h4>
        <ul>
          <li>Point 1...</li>
        </ul>
        
        <h4>⚠️ Areas for Improvement</h4>
        <ul>
          <li>Point 1...</li>
        </ul>
        
        <h4>🛠️ Suggestions & Tips</h4>
        <ul>
          <li>Point 1...</li>
        </ul>
        
        <h4>✨ Optimized Version</h4>
        <blockquote>[Place rewritten prompt text here]</blockquote>
        """
        
        response = model.generate_content(
            prompt_analysis_request,
            generation_config={"temperature": 0.3}
        )
        
        analysis_text = response.text.strip()
        
        # Clean up any potential markdown wraps if the model ignored instructions
        if analysis_text.startswith("```html"):
            analysis_text = analysis_text[7:]
        if analysis_text.endswith("```"):
            analysis_text = analysis_text[:-3]
        analysis_text = analysis_text.strip()
        
        version.ai_feedback = analysis_text
        db.session.commit()
        
        flash(f'Successfully analyzed Version {version.version_number} using AI!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'AI Analysis failed: {str(e)}', 'danger')
        
    return redirect(url_for('prompts.detail', id=version.prompt_id))
