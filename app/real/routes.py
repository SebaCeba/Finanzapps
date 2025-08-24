from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from datetime import datetime
from app.models import db, Categoria, HechoFinanciero
import os

real_bp = Blueprint("real", __name__)

@real_bp.route("/real", strict_slashes=False)
@login_required
def vista_real():
    print("🔥 ENTRO A LA FUNCIÓN REAL")
    print("📂 FUNCION REAL DESDE:", os.path.abspath(__file__))

    # Obtener año desde la URL o usar el actual por defecto
    año_param = request.args.get("año")
    mes_param = request.args.get("mes")
    año_actual = datetime.utcnow().year

    # AÑOS DISPONIBLES
    años = db.session.query(Presupuesto.año.distinct()) \
        .filter(Presupuesto.usuario_id == current_user.id) \
        .order_by(Presupuesto.año).all()
    años = [a[0] for a in años]

    if not años:
        return render_template("real.html", data=[], año=None, mes=None, años=[], meses=[], mensaje="No hay años disponibles con presupuesto.")

    año = int(año_param) if año_param and int(año_param) in años else años[-1]

    # MESES DISPONIBLES para ese año
    meses = db.session.query(Presupuesto.mes.distinct()) \
        .filter(Presupuesto.usuario_id == current_user.id, Presupuesto.año == año) \
        .order_by(Presupuesto.mes).all()
    meses = [m[0] for m in meses]

    print("📆 Meses disponibles:", meses)

    if not meses:
        return render_template("real.html", data=[], año=año, mes=None, años=años, meses=[], mensaje="No hay meses con presupuesto para este año.")

    mes = int(mes_param) if mes_param and int(mes_param) in meses else meses[0]

    # Obtener todas las categorías del usuario
    categorias = Categoria.query.filter_by(usuario_id=current_user.id).all()
    presupuestos = Presupuesto.query.filter_by(usuario_id=current_user.id, año=año, mes=mes).all()

    data = {}
    data_ids = {}
    data_tipos = {}

    for cat in categorias:
        data[cat.nombre] = {
            "presupuesto": 0,
            "real": 0,
        }
        data_ids[cat.nombre] = cat.id
        data_tipos[cat.nombre] = cat.tipo

    for p in presupuestos:
        nombre = next((c.nombre for c in categorias if c.id == p.categoria_id), None)
        if nombre:
            data[nombre]["presupuesto"] = p.monto_presupuestado

    # 🔍 Aquí podrías integrar datos reales desde Transaccion más adelante
    print(f"🧾 Año: {año} - Mes: {mes} - Categorías cargadas: {len(data)}")

    return render_template(
        "real.html",
        año_actual=año,
        año=año,
        mes=mes,
        años=años,
        meses=meses,
        data=data,
        data_ids=data_ids,
        data_tipos=data_tipos,
        mensaje=None
    )
@real_bp.route("/real/guardar", methods=["POST"])
@login_required
def guardar_real():
    # Aquí guardarás tanto presupuesto como real desde los formularios
    # Por ahora solo imprime lo recibido para depuración
    print("📥 POST recibido:", dict(request.form))
    return redirect(url_for('real.vista_real'))
