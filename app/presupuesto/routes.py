from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app.models import db, Categoria, Presupuesto

presupuesto_bp = Blueprint("presupuesto", __name__)

@presupuesto_bp.route("/presupuesto", methods=["GET"])
@login_required
def presupuesto():
    año_actual = datetime.utcnow().year
    año = request.args.get("año", año_actual, type=int)
    años = list(range(año_actual - 1, año_actual + 2))  # ejemplo: [2024, 2025, 2026]

    categorias = Categoria.query.filter_by(usuario_id=current_user.id).all()
    presupuestos = Presupuesto.query.filter_by(usuario_id=current_user.id, año=año).all()

    data = {}
    data_ids = {}

    for cat in categorias:
        data[cat.nombre] = {mes: 0 for mes in range(1, 13)}
        data_ids[cat.nombre] = cat.id

    for p in presupuestos:
        nombre = next((c.nombre for c in categorias if c.id == p.categoria_id), None)
        if nombre:
            data[nombre][p.mes] = p.monto_presupuestado

    return render_template("presupuesto.html", año_actual=año, años=años, data=data, data_ids=data_ids)

@presupuesto_bp.route("/presupuesto/guardar", methods=["POST"])
@login_required
def guardar_presupuesto():
    año = int(request.form.get("año"))
    data = request.form.to_dict(flat=False)

    Presupuesto.query.filter_by(usuario_id=current_user.id, año=año).delete()

    for key in request.form:
        if key.startswith("presupuesto[") and not key.endswith("][nombre]") and "nueva_categoria" not in key:
            partes = key.split("][")
            nombre = partes[0].split("[")[1].strip()
            if not nombre or nombre == "nueva_categoria":
                continue  # ⛔️ salta si no hay nombre o si es la fila vacía
            if "][" in key and not key.endswith("][nombre]"):
                mes = int(partes[1].rstrip("]"))
                monto = float(request.form[key] or 0)

                categoria = Categoria.query.filter_by(nombre=nombre, usuario_id=current_user.id).first()
                if not categoria:
                    categoria = Categoria(nombre=nombre, tipo="gasto_variable", usuario_id=current_user.id)
                    db.session.add(categoria)
                    db.session.flush()  # obtener su ID antes del commit

                nuevo = Presupuesto(
                    usuario_id=current_user.id,
                    categoria_id=categoria.id,
                    año=año,
                    mes=mes,
                    monto_presupuestado=monto
                )
                db.session.add(nuevo)

    db.session.commit()
    flash("Presupuesto actualizado.")
    return redirect(url_for("presupuesto.presupuesto"))

@presupuesto_bp.route("/presupuesto/eliminar", methods=["POST"])
@login_required
def eliminar_categoria():
    categoria_id = request.form.get("categoria_id")

    if categoria_id:
        categoria = Categoria.query.filter_by(id=categoria_id, usuario_id=current_user.id).first()
        if categoria:
            Presupuesto.query.filter_by(categoria_id=categoria.id, usuario_id=current_user.id).delete()
            db.session.delete(categoria)
            db.session.commit()
            flash("Categoría eliminada exitosamente.")
        else:
            flash("Categoría no encontrada.")
    else:
        flash("ID de categoría no proporcionado.")

    return redirect(url_for("presupuesto.presupuesto"))