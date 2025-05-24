import os
import sqlite3
import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

app = Flask(__name__)

# 🔹 RUTA ABSOLUTA DEL PROYECTO
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 🔹 RUTA DEL DIRECTORIO instance/
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)

# 🔹 Ruta final de la base de datos
DB_PATH = os.path.join(INSTANCE_DIR, "finanzas.db")

# 🔹 Configuración de Flask + SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# 🔹 Modelo de Usuario
class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    contraseña = db.Column(db.String(100), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    transacciones = db.relationship('Transaccion', backref='usuario', lazy=True)
    presupuestos = db.relationship('Presupuesto', backref='usuario', lazy=True)
    categorias = db.relationship('Categoria', backref='usuario', lazy=True)

# 🔹 Categorías
class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    tipo = db.Column(db.String(15), nullable=False)  # ingreso, gasto_fijo, gasto_variable
    parent_id = db.Column(db.Integer, db.ForeignKey("categoria.id"), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)

    subcategorias = db.relationship("Categoria", remote_side=[id])

# 🔹 Transacciones
class Transaccion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(15), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categoria.id"), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.String(10), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)

# 🔹 Presupuesto
class Presupuesto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categoria.id"), nullable=False)
    mes = db.Column(db.Integer, nullable=False)
    año = db.Column(db.Integer, nullable=False)
    monto_presupuestado = db.Column(db.Float, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)

# 🔹 Resumen mensual (opcionalmente por usuario)
class ResumenMensual(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mes = db.Column(db.Integer, nullable=False)
    año = db.Column(db.Integer, nullable=False)
    total_ingresos = db.Column(db.Float, default=0)
    total_gastos_fijos = db.Column(db.Float, default=0)
    total_gastos_variables = db.Column(db.Float, default=0)
    # usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))  # si lo haces por usuario

# 🔹 Crear la base si no existe
with app.app_context():
    db.create_all()
    print(f"✅ Base de datos creada en: {DB_PATH}")

# 🔹 Funciones auxiliares para Tkinter o uso externo
def obtener_tipos_desde_bd():
    try:
        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()
        cursor.execute("SELECT DISTINCT tipo FROM categoria")
        tipos = [fila[0] for fila in cursor.fetchall()]
        conexion.close()
        return tipos
    except Exception as e:
        print(f"❌ Error al obtener tipos de la base de datos: {e}")
        return ["ingreso", "gasto_fijo", "gasto_variable", "otro"]

def obtener_categorias_desde_bd():
    try:
        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()
        cursor.execute("SELECT id, nombre FROM categoria ORDER BY nombre")
        categorias = cursor.fetchall()
        conexion.close()
        return categorias
    except Exception as e:
        print(f"❌ Error al obtener categorías de la base de datos: {e}")
        return []