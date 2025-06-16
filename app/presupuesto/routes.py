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
    años = list(range(año_actual - 1, año_actual + 2))  # ej: [2024, 2025, 2026]

    categorias = Categoria.query.filter_by(usuario_id=current_user.id).all()
    presupuestos = Presupuesto.query.filter_by(usuario_id=current_user.id, año=año).all()

    data = {}
    data_ids = {}
    data_tipos = {}

    for cat in categorias:
        data[cat.nombre] = {mes: 0 for mes in range(1, 13)}
        data_ids[cat.nombre] = cat.id
        data_tipos[cat.nombre] = cat.tipo  # <--- Aquí almacenamos el tipo de cada categoría

    for p in presupuestos:
        nombre = next((c.nombre for c in categorias if c.id == p.categoria_id), None)
        if nombre:
            data[nombre][p.mes] = p.monto_presupuestado

    return render_template(
        "presupuesto.html",
        año_actual=año,
        años=años,
        data=data,
        data_ids=data_ids,
        data_tipos=data_tipos,  # <--- lo pasamos al template
    )

@presupuesto_bp.route("/presupuesto/guardar", methods=["POST"])
@login_required
def guardar_presupuesto():
    año = int(request.form.get("año"))
    tipo_actual = request.form.get("tipo_actual")  # 👈 capturamos el tipo_actual del form

    # Eliminamos solo las categorías de este tipo_actual
    categorias = Categoria.query.filter_by(usuario_id=current_user.id, tipo=tipo_actual).all()
    categoria_ids = [c.id for c in categorias]
    if categoria_ids:
        Presupuesto.query.filter(
            Presupuesto.usuario_id == current_user.id,
            Presupuesto.año == año,
            Presupuesto.categoria_id.in_(categoria_ids)
        ).delete(synchronize_session=False)

    for key in request.form:
        if key.startswith("presupuesto["):
            partes = key.split("][")
            nombre = partes[0].split("[")[1]

            # 🔥 Agregamos esta validación
            if not nombre or nombre.lower() == "nueva_categoria" or nombre.strip() == "":
                continue  # ignorar esta fila vacía

            if "][" in key and not key.endswith("][nombre]"):
                mes = int(partes[1].rstrip("]"))
                monto = float(request.form[key] or 0)

                categoria = Categoria.query.filter_by(nombre=nombre, usuario_id=current_user.id).first()
                if not categoria:
                    categoria = Categoria(
                        nombre=nombre.strip(),  # ⚡ limpio el nombre
                        tipo=tipo_actual,
                        usuario_id=current_user.id
                    )
                    db.session.add(categoria)
                    db.session.flush()

                nuevo = Presupuesto(
                    usuario_id=current_user.id,
                    categoria_id=categoria.id,
                    año=año,
                    mes=mes,
                    monto_presupuestado=monto
                )
                db.session.add(nuevo)

    db.session.commit()
    flash("Presupuesto actualizado.", "success")
    return redirect(url_for("presupuesto.presupuesto"))


@presupuesto_bp.route('/presupuesto/eliminar_categoria', methods=['POST'])
@login_required
def eliminar_categoria():
    categoria_id = request.form.get("categoria_id")
    categoria = Categoria.query.filter_by(id=categoria_id, usuario_id=current_user.id).first()
    if categoria:
        # Borra presupuestos asociados antes de borrar la categoría (por integridad referencial)
        Presupuesto.query.filter_by(categoria_id=categoria.id).delete()
        db.session.delete(categoria)
        db.session.commit()
        flash("Categoría eliminada.")
    else:
        flash("Categoría no encontrada.", "error")
    return redirect(url_for("presupuesto.presupuesto"))

@presupuesto_bp.route('/presupuesto/editar_categoria', methods=['POST'])
@login_required
def editar_categoria():
    from flask import jsonify  # Asegúrate de importar jsonify
    categoria_id = request.form.get("categoria_id")
    nuevo_nombre = request.form.get("nuevo_nombre")
    if not categoria_id or not nuevo_nombre:
        return jsonify({"success": False, "message": "Datos incompletos"}), 400
    categoria = Categoria.query.filter_by(id=categoria_id, usuario_id=current_user.id).first()
    if not categoria:
        return jsonify({"success": False, "message": "Categoría no encontrada"}), 404
    categoria.nombre = nuevo_nombre.strip()
    db.session.commit()
    return jsonify({"success": True, "nuevo_nombre": categoria.nombre})

