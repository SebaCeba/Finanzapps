from flask import Blueprint, request, jsonify
from app.extensions import db
from .models import Dimension, Hierarchy, Member, HierarchyEdge, MemberAlias, MemberProperty
from sqlalchemy import and_

bp = Blueprint('dimensions_api', __name__, url_prefix='/api')

# ---------- DIMENSIONS ----------
@bp.get('/dimensions')
def list_dimensions():
    dims = Dimension.query.order_by(Dimension.id).all()
    return jsonify([{
        'id': d.id, 'code': d.code, 'name': d.name,
        'description': d.description, 'is_active': d.is_active
    } for d in dims])

@bp.post('/dimensions')
def create_dimension():
    data = request.get_json() or {}
    code = (data.get('code') or '').strip()
    name = (data.get('name') or '').strip()
    if not code or not name:
        return jsonify({'error': 'code y name son requeridos'}), 400
    exists = Dimension.query.filter_by(code=code).first()
    if exists:
        return jsonify({'error': f'ya existe dimension {code}'}), 400
    d = Dimension(code=code, name=name, is_active=True)
    db.session.add(d)
    db.session.flush()  # para tener d.id
    # crea jerarquía primaria por defecto
    h = Hierarchy(dimension_id=d.id, code='PRIMARY', name='PRIMARY', is_primary=True)
    db.session.add(h)
    db.session.commit()
    return jsonify({'id': d.id}), 201

@bp.put('/dimensions/<int:dim_id>')
def update_dimension(dim_id):
    d = db.session.get(Dimension, dim_id)
    if not d:
        return jsonify({'error': 'dimension no existe'}), 404
    data = request.get_json() or {}
    if 'name' in data:
        d.name = (data['name'] or '').strip() or d.name
    if 'description' in data:
        d.description = (data['description'] or '').strip()
    db.session.commit()
    return jsonify({'ok': True})

@bp.delete('/dimensions/<int:dim_id>')
def delete_dimension(dim_id):
    d = db.session.get(Dimension, dim_id)
    if not d:
        return jsonify({'error': 'dimension no existe'}), 404
    # borrar jerarquías/edges
    hiers = Hierarchy.query.filter_by(dimension_id=dim_id).all()
    for h in hiers:
        HierarchyEdge.query.filter_by(hierarchy_id=h.id).delete()
    Hierarchy.query.filter_by(dimension_id=dim_id).delete()
    # borrar miembros y sus extras
    mems = Member.query.filter_by(dimension_id=dim_id).all()
    for m in mems:
        MemberAlias.query.filter_by(member_id=m.id).delete()
        MemberProperty.query.filter_by(member_id=m.id).delete()
    Member.query.filter_by(dimension_id=dim_id).delete()
    # borrar dimensión
    db.session.delete(d)
    db.session.commit()
    return jsonify({'ok': True})

# ---------- MEMBERS ----------
@bp.get('/dimensions/<int:dim_id>/members')
def list_members(dim_id):
    mems = Member.query.filter_by(dimension_id=dim_id).order_by(Member.code).all()
    return jsonify([{
        'id': m.id, 'code': m.code, 'name': m.name,
        'agg_op': m.agg_op, 'data_type': m.data_type,
        'is_shared': m.is_shared, 'is_active': m.is_active
    } for m in mems])

@bp.post('/dimensions/<int:dim_id>/members')
def create_member(dim_id):
    d = db.session.get(Dimension, dim_id)
    if not d:
        return jsonify({'error': 'dimension no existe'}), 404
    data = request.get_json() or {}
    code = (data.get('code') or '').strip()
    name = (data.get('name') or '').strip()
    agg_op = (data.get('agg_op') or '').strip() or None
    data_type = (data.get('data_type') or '').strip() or None
    if not code or not name:
        return jsonify({'error': 'code y name son requeridos'}), 400
    exists = Member.query.filter_by(dimension_id=dim_id, code=code).first()
    if exists:
        return jsonify({'error': f'ya existe member {code} en dimension {d.code}'}), 400
    m = Member(dimension_id=dim_id, code=code, name=name, agg_op=agg_op,
               data_type=data_type, is_shared=False, is_active=True)
    db.session.add(m)
    db.session.commit()
    return jsonify({'id': m.id}), 201

@bp.put('/members/<int:mem_id>')
def update_member(mem_id):
    m = db.session.get(Member, mem_id)
    if not m:
        return jsonify({'error': 'member no existe'}), 404
    data = request.get_json() or {}
    for field in ('name', 'agg_op', 'data_type'):
        if field in data:
            setattr(m, field, (data[field] or '').strip() or None)
    db.session.commit()
    return jsonify({'ok': True})

@bp.delete('/members/<int:mem_id>')
def delete_member(mem_id):
    m = db.session.get(Member, mem_id)
    if not m:
        return jsonify({'error': 'member no existe'}), 404
    # eliminar edges donde participa
    HierarchyEdge.query.filter(
        (HierarchyEdge.child_member_id == mem_id) | (HierarchyEdge.parent_member_id == mem_id)
    ).delete()
    # borrar extras
    MemberAlias.query.filter_by(member_id=mem_id).delete()
    MemberProperty.query.filter_by(member_id=mem_id).delete()
    db.session.delete(m)
    db.session.commit()
    return jsonify({'ok': True})

# ---------- HIERARCHIES / EDGES ----------
@bp.get('/dimensions/<int:dim_id>/hierarchies')
def list_hierarchies(dim_id):
    hiers = Hierarchy.query.filter_by(dimension_id=dim_id).order_by(Hierarchy.id).all()
    return jsonify([{
        'id': h.id, 'code': h.code, 'name': h.name, 'is_primary': h.is_primary
    } for h in hiers])

@bp.post('/hierarchies/<int:hier_id>/edges')
def create_edge(hier_id):
    h = db.session.get(Hierarchy, hier_id)
    if not h:
        return jsonify({'error': 'hierarchy no existe'}), 404
    data = request.get_json() or {}
    parent_id = data.get('parent_member_id', None)
    child_id = data.get('child_member_id', None)
    order_nbr = data.get('order_nbr', 0) or 0
    unary_op = (data.get('unary_op') or '+').strip()

    if not child_id:
        return jsonify({'error': 'child_member_id es requerido'}), 400

    # evitar duplicados por constraint lógico
    dup = HierarchyEdge.query.filter_by(
        hierarchy_id=hier_id,
        parent_member_id=parent_id,
        child_member_id=child_id
    ).first()
    if dup:
        return jsonify({'error': 'ya existe ese vínculo'}), 400

    e = HierarchyEdge(hierarchy_id=hier_id, parent_member_id=parent_id,
                      child_member_id=child_id, order_nbr=int(order_nbr),
                      unary_op=unary_op)
    db.session.add(e)
    db.session.commit()
    return jsonify({'id': e.id}), 201

@bp.get('/hierarchies/<int:hier_id>/tree')
def get_tree(hier_id):
    edges = HierarchyEdge.query.filter_by(hierarchy_id=hier_id).order_by(HierarchyEdge.order_nbr).all()
    return jsonify([{
        'id': e.id,
        'hierarchy_id': e.hierarchy_id,
        'parent_member_id': e.parent_member_id,
        'child_member_id': e.child_member_id,
        'order_nbr': e.order_nbr,
        'unary_op': e.unary_op
    } for e in edges])

@bp.delete('/edges/<int:edge_id>')
def delete_edge(edge_id):
    e = db.session.get(HierarchyEdge, edge_id)
    if not e:
        return jsonify({'error': 'edge no existe'}), 404
    db.session.delete(e)
    db.session.commit()
    return jsonify({'ok': True})
