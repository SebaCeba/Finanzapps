from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime


db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    contrasena = db.Column(db.String(200), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)


    categorias = db.relationship('Categoria', backref='usuario', lazy=True)
    hechos = db.relationship('HechoFinanciero', backref='usuario', lazy=True)

class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # ingreso o gasto
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    
    hechos = db.relationship('HechoFinanciero', backref='categoria', lazy=True)

class HechoFinanciero(db.Model):
    __tablename__ = 'hecho_financiero'
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), primary_key=True)
    año = db.Column(db.Integer, primary_key=True)
    mes = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), primary_key=True)  # ingreso o gasto
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), primary_key=True)
    tipo = db.Column(db.String(20),nullable=False )  # presupuesto o real
    monto = db.Column(db.Float,nullable=False)

class Presupuesto(db.Model):
    __tablename__ = 'presupuesto'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    mes = db.Column(db.Integer)
    año = db.Column(db.Integer)
    monto_presupuestado = db.Column(db.Float)
    categoria_id = db.Column(db.Integer)
    usuario_id = db.Column(db.Integer)

    
