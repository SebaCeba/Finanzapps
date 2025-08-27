# app/dimensions/api_members.py
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.dimensions.models import Member, HierarchyEdge  # ajusta si tus nombres difieren
from sqlalchemy import text, bindparam


# Nota: SIN url_prefix aquí; lo agregamos al registrar en create_app()
api_members_bp = Blueprint("api_members", __name__)

@api_members_bp.get("/api/members/<int:member_id>")
def get_member(member_id: int):
    m = Member.query.get_or_404(member_id)
    return jsonify({
        "id": m.id,
        "dimension_id": m.dimension_id,
        "code": m.code,
        "name": m.name,
        "agg_op": m.agg_op,
        "is_active": m.is_active
    })

@api_members_bp.put("/api/members/<int:member_id>")
def update_member(member_id: int):
    m = Member.query.get_or_404(member_id)
    data = request.get_json(silent=True) or {}
    # Solo campos permitidos
    for field in ("name", "agg_op", "is_active"):
        if field in data:
            setattr(m, field, data[field])
    db.session.commit()
    return jsonify({"status": "ok"})

@api_members_bp.delete("/api/members/<int:member_id>")
def delete_member(member_id: int):
    from flask import current_app
    from sqlalchemy import text

    m = Member.query.get_or_404(member_id)

    # Log para verificar que sí entramos a ESTE endpoint
    current_app.logger.info(f"[members.delete] Intento de borrar member_id=%s", member_id)

    # Conteo directo en tabla (evita desalineación de nombres de atributos del modelo)
    refs = db.session.execute(
        text("""
            SELECT COUNT(1)
            FROM hierarchy_edges
            WHERE parent_member_id = :id OR child_member_id = :id
        """),
        {"id": member_id}
    ).scalar() or 0

    if refs > 0:
        current_app.logger.info(f"[members.delete] BLOQUEADO: {refs} vínculos para member_id=%s", member_id)
        return jsonify({
            "error": (
                "No se puede eliminar este miembro porque está vinculado en una o más jerarquías. "
                "Primero elimina sus vínculos y luego vuelve a intentarlo."
            )
        }), 400

    db.session.delete(m)
    db.session.commit()
    current_app.logger.info(f"[members.delete] OK: eliminado member_id=%s", member_id)
    return jsonify({"status": "ok"})
@api_members_bp.get("/api/members/usage")
def usage_members():
    """
    Devuelve cuántos vínculos (edges) tiene cada member_id pedido.
    GET /api/members/usage?ids=1,2,3
    Respuesta: {"1": 2, "2": 0, "3": 5}
    """
    ids_param = (request.args.get("ids") or "").strip()
    if not ids_param:
        return jsonify({})

    # Parseo seguro a enteros
    try:
        ids = [int(x) for x in ids_param.split(",") if x.strip().isdigit()]
    except ValueError:
        return jsonify({})

    if not ids:
        return jsonify({})

    # Contar parent + child en una sola pasada y filtrar por IN (expanding)
    sql = text("""
        SELECT t.mid AS mid, COUNT(1) AS edges
        FROM (
          SELECT parent_member_id AS mid FROM hierarchy_edges
          UNION ALL
          SELECT child_member_id  AS mid FROM hierarchy_edges
        ) AS t
        WHERE t.mid IN :ids
        GROUP BY t.mid
    """).bindparams(bindparam("ids", expanding=True))

    rows = db.session.execute(sql, {"ids": ids}).all()
    data = {str(r.mid): int(r.edges) for r in rows}
    # Asegurar que todos los ids vengan en la respuesta (0 si no tienen vínculos)
    for i in ids:
        data.setdefault(str(i), 0)
    return jsonify(data)
