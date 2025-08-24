from flask import Blueprint, request, jsonify
from app.extensions import db
from .models import Dimension, Member, Hierarchy, HierarchyEdge, MemberAlias, MemberProperty
from .services import has_cycle, DimensionError

bp = Blueprint('dimensions', __name__, url_prefix='/api')

# --------- DIMENSIONS ---------
@bp.get('/dimensions')
def list_dimensions():
    dims = Dimension.query.order_by(Dimension.code).all()
    return jsonify([{
        'id': d.id, 'code': d.code, 'name': d.name,
        'description': d.description, 'is_active': d.is_active
    } for d in dims])

@bp.post('/dimensions')
def create_dimension():
    data = request.get_json() or {}
    d = Dimension(code=data['code'].strip(), name=data.get('name', data['code']).strip(),
                  description=data.get('description'))
    db.session.add(d)
    db.session.commit()
    # crear jerarquía primaria por defecto
    h = Hierarchy(dimension_id=d.id, code='PRIMARY', name='Primary', is_primary=True)
    db.session.add(h)
    db.session.commit()
    return jsonify({'id': d.id}), 201

@bp.put('/dimensions/<int:dim_id>')
def update_dimension(dim_id):
    d = Dimension.query.get_or_404(dim_id)
    data = request.get_json() or {}
    d.name = data.get('name', d.name)
    d.description = data.get('description', d.description)
    d.is_active = bool(data.get('is_active', d.is_active))
    db.session.commit()
    return jsonify({'ok': True})

@bp.delete('/dimensions/<int:dim_id>')
def delete_dimension(dim_id):
    d = Dimension.query.get_or_404(dim_id)
    db.session.delete(d)
    db.session.commit()
    return jsonify({'ok': True})

# --------- MEMBERS ---------
@bp.get('/dimensions/<int:dim_id>/members')
def list_members(dim_id):
    q = Member.query.filter_by(dimension_id=dim_id).order_by(Member.code)
    return jsonify([{'id': m.id, 'code': m.code, 'name': m.name, 'agg_op': m.agg_op, 'data_type': m.data_type,
                     'is_active': m.is_active} for m in q.all()])

@bp.post('/dimensions/<int:dim_id>/members')
def create_member(dim_id):
    data = request.get_json() or {}
    m = Member(dimension_id=dim_id, code=data['code'].strip(), name=data.get('name', data['code']).strip(),
               agg_op=data.get('agg_op','+'), data_type=data.get('data_type'))
    db.session.add(m)
    db.session.commit()
    return jsonify({'id': m.id}), 201

@bp.put('/members/<int:member_id>')
def update_member(member_id):
    m = Member.query.get_or_404(member_id)
    data = request.get_json() or {}
    m.name = data.get('name', m.name)
    m.agg_op = data.get('agg_op', m.agg_op)
    m.data_type = data.get('data_type', m.data_type)
    m.is_active = bool(data.get('is_active', m.is_active))
    db.session.commit()
    return jsonify({'ok': True})

@bp.delete('/members/<int:member_id>')
def delete_member(member_id):
    m = Member.query.get_or_404(member_id)
    db.session.delete(m)
    db.session.commit()
    return jsonify({'ok': True})

# --------- HIERARCHIES ---------
@bp.get('/dimensions/<int:dim_id>/hierarchies')
def list_hier(dim_id):
    hs = Hierarchy.query.filter_by(dimension_id=dim_id).order_by(Hierarchy.code).all()
    return jsonify([{'id': h.id, 'code': h.code, 'name': h.name, 'is_primary': h.is_primary} for h in hs])

@bp.post('/dimensions/<int:dim_id>/hierarchies')
def create_hier(dim_id):
    data = request.get_json() or {}
    h = Hierarchy(dimension_id=dim_id, code=data['code'].strip(), name=data.get('name','').strip() or data['code'])
    db.session.add(h)
    db.session.commit()
    return jsonify({'id': h.id}), 201

# --------- EDGES (padre-hijo) ---------
@bp.get('/hierarchies/<int:h_id>/tree')
def get_tree(h_id):
    # Devuelve lista de aristas y miembros para pintar un arbol en frontend
    edges = HierarchyEdge.query.filter_by(hierarchy_id=h_id).order_by(HierarchyEdge.order_nbr).all()
    return jsonify([{'id': e.id, 'parent_member_id': e.parent_member_id, 'child_member_id': e.child_member_id,
                    'order_nbr': e.order_nbr, 'unary_op': e.unary_op} for e in edges])

@bp.post('/hierarchies/<int:h_id>/edges')
def add_edge(h_id):
    data = request.get_json() or {}
    e = HierarchyEdge(hierarchy_id=h_id, parent_member_id=data.get('parent_member_id'),
                      child_member_id=data['child_member_id'], order_nbr=int(data.get('order_nbr',0)),
                      unary_op=data.get('unary_op','+'))
    db.session.add(e)
    db.session.commit()

    if has_cycle(h_id):
        db.session.delete(e)
        db.session.commit()
        return jsonify({'ok': False, 'error': 'Ciclo detectado en la jerarquía'}), 400
    return jsonify({'id': e.id}), 201

@bp.delete('/edges/<int:edge_id>')
def delete_edge(edge_id):
    e = HierarchyEdge.query.get_or_404(edge_id)
    db.session.delete(e)
    db.session.commit()
    return jsonify({'ok': True})

# --------- ALIAS ---------
@bp.put('/members/<int:member_id>/alias')
def upsert_alias(member_id):
    data = request.get_json() or {}
    tab = (data.get('alias_tab') or 'Default').strip()
    val = (data.get('alias_val') or '').strip()
    a = MemberAlias.query.filter_by(member_id=member_id, alias_tab=tab).first()
    if a:
        a.alias_val = val
    else:
        a = MemberAlias(member_id=member_id, alias_tab=tab, alias_val=val)
        db.session.add(a)
    db.session.commit()
    return jsonify({'ok': True})

# --------- PROPIEDADES ---------
@bp.put('/members/<int:member_id>/property')
def upsert_property(member_id):
    data = request.get_json() or {}
    key = data['prop_key'].strip()
    val = (data.get('prop_val') or '').strip()
    p = MemberProperty.query.filter_by(member_id=member_id, prop_key=key).first()
    if p:
        p.prop_val = val
    else:
        p = MemberProperty(member_id=member_id, prop_key=key, prop_val=val)
        db.session.add(p)
    db.session.commit()
    return jsonify({'ok': True})