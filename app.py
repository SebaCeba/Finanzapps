from flask import Flask, render_template, redirect, url_for, request, flash
from database import db, Transaccion, ResumenMensual, Categoria, Presupuesto, Usuario
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from datetime import datetime

# 🔹 Configuración Flask
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///finanzas.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# 🔹 Login Manager
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# 🔹 Ruta de bienvenida pública
@app.route("/")
def bienvenida():
    if current_user.is_authenticated:
        return redirect(url_for("panel"))
    return render_template("bienvenida.html")

# 🔹 Panel principal con días activos
@app.route("/panel")
@login_required
def panel():
    dias_activo = (datetime.utcnow() - current_user.fecha_creacion).days
    return render_template("index.html", nombre=current_user.nombre, dias=dias_activo)

# 🔹 Registro de usuario
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

# 🔹 Login
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

# 🔹 Transacciones del usuario
@app.route("/transacciones")
@login_required
def transacciones():
    transacciones = Transaccion.query.filter_by(usuario_id=current_user.id).all()
    return render_template("transacciones.html", transacciones=transacciones)

# 🔹 Vista de categorías y subcategorías
@app.route("/categorias")
@login_required
def mostrar_categorias():
    categorias = Categoria.query.filter_by(parent_id=None, usuario_id=current_user.id).all()
    subcategorias = Categoria.query.filter(Categoria.parent_id.isnot(None), Categoria.usuario_id == current_user.id).all()
    return render_template("categorias.html", categorias=categorias, subcategorias=subcategorias)

# 🔹 Panel de administración (opcional)
@app.route("/admin")
@login_required
def admin_dashboard():
    return render_template("admin.html",
        total_categorias=Categoria.query.count(),
        total_subcategorias=Categoria.query.filter(Categoria.parent_id.isnot(None)).count(),
        total_transacciones=Transaccion.query.count(),
        total_presupuestos=Presupuesto.query.count(),
        total_resumenes=ResumenMensual.query.count()
    )

# 🔹 Página de presupuesto anual
@app.route("/presupuesto", methods=["GET"])
@login_required
def presupuesto():
    año_actual = datetime.now().year

    años_disponibles = (
        db.session.query(Presupuesto.año)
        .filter_by(usuario_id=current_user.id)
        .distinct()
        .order_by(Presupuesto.año)
        .all()
    )
    años = [a[0] for a in años_disponibles] or [año_actual]

    categorias_ingreso = Categoria.query.filter_by(
        tipo="ingreso", usuario_id=current_user.id
    ).all()

    presupuestos = Presupuesto.query.filter_by(usuario_id=current_user.id).all()

    data = {}
    data_ids = {}
    for cat in categorias_ingreso:
        data[cat.nombre] = {mes: 0 for mes in range(1, 13)}
        data_ids[cat.nombre] = cat.id
        for p in presupuestos:
            if p.categoria_id == cat.id:
                data[cat.nombre][p.mes] = p.monto_presupuestado

    return render_template("presupuesto.html", años=años, año_actual=año_actual, data=data, data_ids=data_ids)

# 🔹 Guardar presupuesto
@app.route("/presupuesto/guardar", methods=["POST"])
@login_required
def guardar_presupuesto():
    año = int(request.form.get("año"))

    for key in request.form:
        if key.startswith("presupuesto"):
            import re
            match = re.match(r"presupuesto\[(.+?)\]\[(\d{1,2})\]", key)
            if match:
                categoria_nombre = match.group(1)
                mes = int(match.group(2))

                # 🛑 Ignorar fila si no fue confirmada
                if categoria_nombre.lower().startswith("nueva_categoria") and f"presupuesto[{categoria_nombre}][nombre]" not in request.form:
                    continue

                try:
                    monto = float(request.form[key])
                except:
                    monto = 0

                categoria = Categoria.query.filter_by(
                    nombre=categoria_nombre,
                    tipo="ingreso",
                    usuario_id=current_user.id
                ).first()

                if not categoria:
                    categoria = Categoria(
                        nombre=categoria_nombre,
                        tipo="ingreso",
                        usuario_id=current_user.id
                    )
                    db.session.add(categoria)
                    db.session.commit()

                presupuesto = Presupuesto.query.filter_by(
                    usuario_id=current_user.id,
                    categoria_id=categoria.id,
                    mes=mes,
                    año=año
                ).first()

                if not presupuesto:
                    presupuesto = Presupuesto(
                        usuario_id=current_user.id,
                        categoria_id=categoria.id,
                        mes=mes,
                        año=año,
                        monto_presupuestado=monto
                    )
                    db.session.add(presupuesto)
                else:
                    presupuesto.monto_presupuestado = monto

    db.session.commit()
    flash("✅ Presupuesto guardado correctamente.")
    return redirect(url_for("presupuesto"))

# 🔹 Eliminar categoría
@app.route("/categoria/eliminar", methods=["POST"])
@login_required
def eliminar_categoria():
    categoria_id = request.form.get("categoria_id")
    categoria = Categoria.query.filter_by(id=categoria_id, usuario_id=current_user.id).first()

    if categoria:
        Presupuesto.query.filter_by(categoria_id=categoria.id, usuario_id=current_user.id).delete()
        db.session.delete(categoria)
        db.session.commit()
        flash("Categoría eliminada correctamente.")
    else:
        flash("No se pudo eliminar la categoría.")

    return redirect(url_for("presupuesto"))

# 🔹 Vista real (placeholder)
@app.route("/real")
@login_required
def real():
    dias_activo = (datetime.utcnow() - current_user.fecha_creacion).days
    return render_template("real.html", nombre=current_user.nombre, dias=dias_activo, activo="real")

# 🔹 Ejecutar localmente
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
