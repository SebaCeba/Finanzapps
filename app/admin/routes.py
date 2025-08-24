from flask import Blueprint, render_template

admin_bp = Blueprint('admin', __name__)

@admin_bp.get('/admin/dimensions')
def admin_dimensions():
    return render_template('dimensions/index.html')
