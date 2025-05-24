from flask import Flask, render_template, redirect, url_for, request, flash
from database import db, Transaccion, ResumenMensual, Categoria, Presupuesto, Usuario
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

# 🔹 Configuración Flask
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///finanzas.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# 🔹 Configurar Login
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


# 🔹 Página de Bienvenida Pública
@app.route("/")
def bienvenida():
    if current_user.is_authenticated:
        return redirect(url_for("panel"))
    return render_template("bienvenida.html")


# 🔹 Panel Principal estilo Fintual (requiere login)
@app.route("/panel")
@login_required
def panel():
    # Calcula los días desde que el usuario creó su cuenta
    dias_activo = (datetime.utcnow() - current_user.fecha_creacion).days

    # Renderiza el panel con los datos dinámicos
    return render_template(
        "index.html",        # Usa tu nuevo index.html con estilo Fintual
        nombre=current_user.nombre,
        dias=dias_activo
    )

# 🔹 Página de Registro
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
            contraseña=generate_password_hash(contraseña, method="pbkdf2:sha256")
            fecha_creacion=datetime.utcnow()
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash("Cuenta creada con éxito. Inicia sesión.")
        return redirect(url_for("login"))
    return render_template("registro.html")


# 🔹 Página de Login
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


# 🔹 Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# 🔹 Página de Transacciones
@app.route("/transacciones")
@login_required
def transacciones():
    transacciones = Transaccion.query.filter_by(usuario_id=current_user.id).all()
    return render_template("transacciones.html", transacciones=transacciones)


# 🔹 Página de Categorías
@app.route("/categorias")
@login_required
def mostrar_categorias():
    categorias = Categoria.query.filter_by(parent_id=None, usuario_id=current_user.id).all()
    subcategorias = Categoria.query.filter(Categoria.parent_id.isnot(None), Categoria.usuario_id == current_user.id).all()
    return render_template("categorias.html", categorias=categorias, subcategorias=subcategorias)


# 🔹 Página Admin
@app.route("/admin")
@login_required
def admin_dashboard():
    total_categorias = Categoria.query.count()
    total_subcategorias = Categoria.query.filter(Categoria.parent_id.isnot(None)).count()
    total_transacciones = Transaccion.query.count()
    total_presupuestos = Presupuesto.query.count()
    total_resumenes = ResumenMensual.query.count()

    return render_template("admin.html",
        total_categorias=total_categorias,
        total_subcategorias=total_subcategorias,
        total_transacciones=total_transacciones,
        total_presupuestos=total_presupuestos,
        total_resumenes=total_resumenes
    )


# 🔹 Ejecutar localmente
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)