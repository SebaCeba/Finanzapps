from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime

dashboard_bp = Blueprint("dashboard", __name__)

# Página pública de bienvenida
@dashboard_bp.route("/")
def bienvenida():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.panel"))
    return render_template("bienvenida.html")

# Panel principal (requiere login)
@dashboard_bp.route("/panel")
@login_required
def panel():
    dias_activo = (datetime.utcnow() - current_user.fecha_creacion).days
    return render_template("index.html", nombre=current_user.nombre, dias=dias_activo, activo="resumen")