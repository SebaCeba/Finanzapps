from datetime import datetime
from sqlalchemy import UniqueConstraint
from app.extensions import db  # <-- usa el db central del proyecto

class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Dimension(db.Model, TimestampMixin):
    __tablename__ = 'dimensions'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    members = db.relationship('Member', backref='dimension', lazy=True, cascade='all, delete-orphan')
    hierarchies = db.relationship('Hierarchy', backref='dimension', lazy=True, cascade='all, delete-orphan')

class Member(db.Model, TimestampMixin):
    __tablename__ = 'members'
    id = db.Column(db.Integer, primary_key=True)
    dimension_id = db.Column(db.Integer, db.ForeignKey('dimensions.id'), nullable=False)
    code = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(256), nullable=False)
    agg_op = db.Column(db.String(2), default='+')
    data_type = db.Column(db.String(64))
    is_shared = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

    __table_args__ = (UniqueConstraint('dimension_id','code', name='uq_member_dim_code'),)

    aliases = db.relationship('MemberAlias', backref='member', lazy=True, cascade='all, delete-orphan')
    properties = db.relationship('MemberProperty', backref='member', lazy=True, cascade='all, delete-orphan')

class Hierarchy(db.Model, TimestampMixin):
    __tablename__ = 'hierarchies'
    id = db.Column(db.Integer, primary_key=True)
    dimension_id = db.Column(db.Integer, db.ForeignKey('dimensions.id'), nullable=False)
    code = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    is_primary = db.Column(db.Boolean, default=True, nullable=False)

    __table_args__ = (UniqueConstraint('dimension_id','code', name='uq_hier_dim_code'),)

    edges = db.relationship('HierarchyEdge', backref='hierarchy', lazy=True, cascade='all, delete-orphan')

class HierarchyEdge(db.Model, TimestampMixin):
    __tablename__ = 'hierarchy_edges'
    id = db.Column(db.Integer, primary_key=True)
    hierarchy_id = db.Column(db.Integer, db.ForeignKey('hierarchies.id'), nullable=False)
    parent_member_id = db.Column(db.Integer, db.ForeignKey('members.id'))
    child_member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    order_nbr = db.Column(db.Integer, default=0, nullable=False)
    unary_op = db.Column(db.String(2), default='+')

    parent = db.relationship('Member', foreign_keys=[parent_member_id], lazy='joined')
    child = db.relationship('Member', foreign_keys=[child_member_id], lazy='joined')

    __table_args__ = (UniqueConstraint('hierarchy_id','parent_member_id','child_member_id', name='uq_edge_unique'),)

class MemberAlias(db.Model, TimestampMixin):
    __tablename__ = 'member_aliases'
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    alias_tab = db.Column(db.String(64), nullable=False, default='Default')
    alias_val = db.Column(db.String(256), nullable=False)

    __table_args__ = (UniqueConstraint('member_id','alias_tab', name='uq_member_alias_tab'),)

class MemberProperty(db.Model, TimestampMixin):
    __tablename__ = 'member_properties'
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    prop_key = db.Column(db.String(64), nullable=False)
    prop_val = db.Column(db.String(256))

    __table_args__ = (UniqueConstraint('member_id','prop_key', name='uq_member_prop_key'),)