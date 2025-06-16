from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.models import Presupuesto, Categoria, Transaccion, db
from sqlalchemy import func

real_bp = Blueprint("real", __name__)

@real_bp.route("/real")
@login_required
def vista_real():
    # Obtener año y mes desde parámetros o usar los primeros disponibles
    año_param = request.args.get("año")
    mes_param = request.args.get("mes")

    # Obtener años disponibles desde presupuesto
    años_disponibles = db.session.query(Presupuesto.año.distinct()).order_by(Presupuesto.año).all()
    años_disponibles = [a[0] for a in años_disponibles]

    if not años_disponibles:
        return render_template("real.html", data=[], año=None, mes=None, años=[], meses=[])

    año = int(año_param) if año_param else años_disponibles[-1]

    # Obtener meses disponibles para ese año
    meses_disponibles = db.session.query(Presupuesto.mes.distinct()).filter_by(año=año).order_by(Presupuesto.mes).all()
    meses_disponibles = [m[0] for m in meses_disponibles]
    mes = int(mes_param) if mes_param else meses_disponibles[0]

    # Obtener presupuestos activos para ese año y mes
    presupuestos = db.session.query(
        Presupuesto.categoria_id,
        Presupuesto.monto_presupuestado,
        Categoria.nombre,
        Categoria.tipo,
        Categoria.parent_id
    ).join(Categoria).filter(
        Presupuesto.año == año,
        Presupuesto.mes == mes
    ).all()

    # Agrupar por categoría padre
    data_por_padre = {}
    for cat_id, monto_ppto, nombre, tipo, parent_id in presupuestos:
        if parent_id is None:
            continue
        padre = Categoria.query.get(parent_id)
        if padre.nombre not in data_por_padre:
            data_por_padre[padre.nombre] = {
                "nombre": padre.nombre,
                "id": padre.id,
                "subcategorias": []
            }

        real_monto = db.session.query(func.sum(Transaccion.monto)).filter_by(
            categoria_id=cat_id,
            tipo=tipo,
            user_id=current_user.id
        ).filter(
            func.strftime("%Y", Transaccion.fecha) == str(año),
            func.strftime("%m", Transaccion.fecha) == f"{mes:02d}"
        ).scalar() or 0

        data_por_padre[padre.nombre]["subcategorias"].append({
            "id": cat_id,
            "nombre": nombre,
            "presupuesto": monto_ppto,
            "real": real_monto
        })
