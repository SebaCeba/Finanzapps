from app import create_app
from app.models import db, Presupuesto, HechoFinanciero

app = create_app()
app.app_context().push()

registros_insertados = 0

presupuestos = Presupuesto.query.all()

for p in presupuestos:
    existe = HechoFinanciero.query.filter_by(
        usuario_id=p.usuario_id,
        categoria_id=p.categoria_id,
        año=p.año,
        mes=p.mes,
        tipo='gasto',
        escenario='presupuesto'
    ).first()

    if not existe:
        nuevo = HechoFinanciero(
            usuario_id=p.usuario_id,
            categoria_id=p.categoria_id,
            año=p.año,
            mes=p.mes,
            tipo='gasto',
            escenario='presupuesto',
            monto=p.monto_presupuestado
        )
        db.session.add(nuevo)
        registros_insertados += 1

db.session.commit()
print(f"✅ Migración completada: {registros_insertados} registros insertados.")