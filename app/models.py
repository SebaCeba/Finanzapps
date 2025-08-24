# app/models.py
from datetime import datetime
from flask_login import UserMixin
from app.extensions import db  # <- usa el db único del proyecto

# Opcional: si vas a tipar relaciones a Member sin importar el módulo
# from app.dimensions.models import Member  # no es obligatorio; usamos string 'Member' abajo

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    contrasena = db.Column(db.String(200), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    categorias = db.relationship('Categoria', backref='usuario', lazy=True)
    hechos = db.relationship('HechoFinanciero', backref='usuario', lazy=True)

# --- Compatibilidad temporal (puedes deprecar luego) ---
class Categoria(db.Model):
    __tablename__ = 'categoria'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # ingreso o gasto
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    hechos = db.relationship('HechoFinanciero', backref='categoria', lazy=True)

# --- Hechos gobernados por dimensiones (members.id) ---
class HechoFinanciero(db.Model):
    __tablename__ = 'hecho_financiero'

    id = db.Column(db.Integer, primary_key=True)  # PK simple para reducir fricción
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    # Dimensiones (FK a members.id)
    account_id    = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    entity_id     = db.Column(db.Integer, db.ForeignKey('members.id'))  # opcional
    costcenter_id = db.Column(db.Integer, db.ForeignKey('members.id'))  # opcional
    scenario_id   = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    time_id       = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)

    # Compatibilidad con tu modelo anterior (puedes hacerla nullable=True y deprecar luego)
    categoria_id  = db.Column(db.Integer, db.ForeignKey('categoria.id'))

    # Datos del hecho
    # Usa NUMERIC para evitar errores de redondeo. En UI/formato muestra con coma (,)
    monto   = db.Column(db.Numeric(18, 2), nullable=False)
    moneda  = db.Column(db.String(10), default='CLP')

    # Relaciones “nombradas” a Member (evita ambigüedad al tener varias FKs a la misma tabla)
    account    = db.relationship('Member', foreign_keys=[account_id])
    entity     = db.relationship('Member', foreign_keys=[entity_id])
    costcenter = db.relationship('Member', foreign_keys=[costcenter_id])
    scenario   = db.relationship('Member', foreign_keys=[scenario_id])
    time       = db.relationship('Member', foreign_keys=[time_id])

class Presupuesto(db.Model):
    __tablename__ = 'presupuesto'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    mes = db.Column(db.Integer)
    año = db.Column(db.Integer)

    # Recomendación: Numeric en lugar de Float
    monto_presupuestado = db.Column(db.Numeric(18, 2))

    categoria_id = db.Column(db.Integer)  # si migras a dimensiones, reemplaza por account_id + scenario_id
    usuario_id = db.Column(db.Integer)
