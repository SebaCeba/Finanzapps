from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets
import os

# 🔹 Modelos y base de datos
from database import db, Usuario, Categoria, Transaccion, Presupuesto, ResumenMensual

# 🔹 Crear app Flask
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "instance", "finanzas.db")

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))
app.secret_key = secrets.token_hex(16)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# 🔹 Crear base de datos si no existe
with app.app_context():
    if not os.path.exists(DB_PATH):
        print("🧹 Base anterior no encontrada. Se creará una nueva.")
    db.create_all()
    print("✅ Base de datos inicializada correctamente.")
    print("📦 Ruta activa:", DB_PATH)

# 🔹 Configurar login
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# 🔹 Ruta: Bienvenida
@app.route("/")
def bienvenida():
    if current_user.is_authenticated:
        return redirect(url_for("panel"))
    return render_template("bienvenida.html")

# 🔹 Ruta: Panel (protegido)
@app.route("/panel")
@login_required
def panel():
    dias_activo = (datetime.utcnow() - current_user.fecha_creacion).days
    return render_template("index.html", nombre=current_user.nombre, dias=dias_activo)

# 🔹 Ruta: Registro
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"]
        email = request.form["email"]
        contraseña = request.form["contraseña"]
        if Usuario.query.filter_by(email=email).first():
            flash("El correo ya está registrado.")
            return redirect(url_for("registro"))
        nuevo_usuario = Usuario(
            nombre=nombre,
            email=email,
            contraseña=generate_password_hash(contraseña, method="pbkdf2:sha256"),
            fecha_creacion=datetime.utcnow()
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash("Cuenta creada con éxito. Inicia sesión.")
        return redirect(url_for("login"))
    return render_template("registro.html")

# 🔹 Ruta: Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        contraseña = request.form["contraseña"]
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and check_password_hash(usuario.contraseña, contraseña):
            login_user(usuario)
            return redirect(url_for("panel"))
        flash("Credenciales incorrectas")
    return render_template("login.html")

# 🔹 Ruta: Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# 🔹 Ejecutar
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
