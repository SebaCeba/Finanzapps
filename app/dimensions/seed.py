from app.extensions import db
from .models import Dimension, Member, Hierarchy

def seed_dimensions():
    base_dims = [
        ('ACCOUNT','Account'),
        ('ENTITY','Entity'),
        ('COSTCENTER','Cost Center'),
        ('SCENARIO','Scenario'),
        ('TIME','Time'),
    ]
    for code, name in base_dims:
        if not Dimension.query.filter_by(code=code).first():
            d = Dimension(code=code, name=name)
            db.session.add(d)
            db.session.flush()
            h = Hierarchy(dimension_id=d.id, code='PRIMARY', name='Primary', is_primary=True)
            db.session.add(h)
    db.session.commit()