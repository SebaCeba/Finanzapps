from flask import Flask, render_template, redirect, url_for, request, flash
from database import db, Transaccion, ResumenMensual, Categoria, Presupuesto, Usuario
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from datetime import datetime

# 🔹 Configuración Flask
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "instance", "finanzas.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
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
            contraseña=generate_password_hash(contraseña, method="pbkdf2:sha256"),
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

@app.route("/presupuesto")
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

    # 🧠 Cargar data y sus IDs
    data = {}
    data_ids = {}
    for cat in categorias_ingreso:
        data[cat.nombre] = {mes: 0 for mes in range(1, 13)}
        data_ids[cat.nombre] = cat.id
        for p in presupuestos:
            if p.categoria_id == cat.id:
                data[cat.nombre][p.mes] = p.monto_presupuestado

    # ✅ Devuelve data y data_ids a la plantilla
    return render_template("presupuesto.html", años=años, año_actual=año_actual, data=data, data_ids=data_ids)


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

@app.route("/categoria/eliminar", methods=["POST"])
@login_required
def eliminar_categoria():
    categoria_id = request.form.get("categoria_id")
    categoria = Categoria.query.filter_by(id=categoria_id, usuario_id=current_user.id).first()
    
    if categoria:
        # Elimina presupuestos relacionados primero
        Presupuesto.query.filter_by(categoria_id=categoria.id, usuario_id=current_user.id).delete()
        db.session.delete(categoria)
        db.session.commit()
        flash("Categoría eliminada correctamente.")
    else:
        flash("No se pudo eliminar la categoría.")

    return redirect(url_for("presupuesto"))


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