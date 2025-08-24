from flask_login import UserMixin
from datetime import datetime
from app.extensions import db

class Usuario(UserMixin, db.Model):
    __tablename__ = "usuario"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    contrasena = db.Column(db.String(200), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    categorias = db.relationship('Categoria', backref='usuario', lazy=True)
    hechos = db.relationship('HechoFinanciero', backref='usuario', lazy=True)

class Categoria(db.Model):
    __tablename__ = "categoria"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # ingreso | gasto
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    hechos = db.relationship('HechoFinanciero', backref='categoria', lazy=True)

class HechoFinanciero(db.Model):
    __tablename__ = 'hecho_financiero'
    id = db.Column(db.Integer, primary_key=True)

    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=True)

    # Referencias a members.id (dimensiones)
    account_id    = db.Column(db.Integer, db.ForeignKey('members.id'),   nullable=True)
    entity_id     = db.Column(db.Integer, db.ForeignKey('members.id'),   nullable=True)
    costcenter_id = db.Column(db.Integer, db.ForeignKey('members.id'),   nullable=True)
    scenario_id   = db.Column(db.Integer, db.ForeignKey('members.id'),   nullable=True)
    time_id       = db.Column(db.Integer, db.ForeignKey('members.id'),   nullable=True)

    moneda = db.Column(db.String(10))
    monto = db.Column(db.Numeric(18, 2), nullable=False)

class Presupuesto(db.Model):
    __tablename__ = 'presupuesto'
    id = db.Column(db.Integer, primary_key=True)
    mes = db.Column(db.Integer)
    año = db.Column(db.Integer)
    monto_presupuestado = db.Column(db.Numeric(18, 2))
    categoria_id = db.Column(db.Integer)
    usuario_id = db.Column(db.Integer)
