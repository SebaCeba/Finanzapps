from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user
from app.models import db, Usuario
from datetime import datetime


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"]
        email = request.form["email"]
        contrasena = request.form["contraseña"]  # Sigue usando "contraseña" porque viene del formulario

        if Usuario.query.filter_by(email=email).first():
            flash("El correo ya está registrado.")
            return redirect(url_for("auth.registro"))

        nuevo_usuario = Usuario(
            nombre=nombre,
            email=email,
            contrasena=generate_password_hash(contrasena),  # ✅ Usa el nombre correcto del campo
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash("Cuenta creada con éxito. Inicia sesión.")
        return redirect(url_for("auth.login"))

    return render_template("registro.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        contrasena = request.form["contraseña"]  # Sigue viniendo del form
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.contrasena, contrasena):  # ✅ Mismo cambio aquí
            login_user(usuario)
            return redirect(url_for("dashboard.panel"))
        else:
            flash("Credenciales incorrectas")

    return render_template("login.html")
