from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import HechoFinanciero
from app.dimensions.utils import parse_decimal_comma, get_member_id

facts_bp = Blueprint('facts', __name__, url_prefix='/api')

@facts_bp.post('/facts')
def create_fact():
    data = request.get_json() or {}

    try:
        usuario_id = int(data['usuario_id'])
        monto = parse_decimal_comma(data['monto'])
        if monto is None:
            return jsonify({'ok': False, 'error': 'monto requerido'}), 400

        categoria_id = data.get('categoria_id')
        if categoria_id is not None:
            categoria_id = int(categoria_id)

        moneda = (data.get('moneda') or '').strip() or None

        account_id    = get_member_id('ACCOUNT',    data.get('account_code'))
        entity_id     = get_member_id('ENTITY',     data.get('entity_code'))
        costcenter_id = get_member_id('COSTCENTER', data.get('costcenter_code'))
        scenario_id   = get_member_id('SCENARIO',   data.get('scenario_code'))
        time_id       = get_member_id('TIME',       data.get('time_code'))

        hf = HechoFinanciero(
            usuario_id=usuario_id,
            categoria_id=categoria_id,
            account_id=account_id,
            entity_id=entity_id,
            costcenter_id=costcenter_id,
            scenario_id=scenario_id,
            time_id=time_id,
            moneda=moneda,
            monto=monto
        )
        db.session.add(hf)
        db.session.commit()
        return jsonify({'id': hf.id}), 201

    except KeyError as e:
        db.session.rollback()
        return jsonify({'ok': False, 'error': f'falta campo requerido: {e}'}), 400
    except ValueError as e:
        db.session.rollback()
        return jsonify({'ok': False, 'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'ok': False, 'error': f'error inesperado: {e}'}), 500
