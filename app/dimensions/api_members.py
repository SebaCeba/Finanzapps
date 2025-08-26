# app/dimensions/api_members.py
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.dimensions.models import Member, HierarchyEdge  # ajusta si tus nombres difieren

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
    m = Member.query.get_or_404(member_id)

    # Seguro: no borrar si aparece en alguna jerarquía (como padre o como hijo)
    refs = (
        db.session.query(HierarchyEdge.id)
        .filter(
            (HierarchyEdge.parent_member_id == member_id) |
            (HierarchyEdge.child_member_id == member_id)
        )
        .count()
    )
    if refs > 0:
        return jsonify({
            "error": (
                "No se puede eliminar este miembro porque está vinculado en una o más jerarquías. "
                "Primero elimina sus vínculos y luego vuelve a intentarlo."
            )
        }), 400

    db.session.delete(m)
    db.session.commit()
    return jsonify({"status": "ok"})
