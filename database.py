import os
import sqlite3
import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 🔹 OBTENER LA RUTA ABSOLUTA DEL PROYECTO
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Esto apunta al directorio del proyecto

# 🔹 RUTA CORRECTA PARA `instance/`
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)  # Crear 'instance/' si no existe

# 🔹 RUTA FINAL DE `finanzas.db`
DB_PATH = os.path.join(INSTANCE_DIR, "finanzas.db")

# 🔹 CONFIGURAR FLASK PARA USAR ESTA BASE DE DATOS
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# 🔹 Tabla de Categorías
class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    tipo = db.Column(db.String(15), nullable=False)  # "ingreso", "gasto_fijo", "gasto_variable"
    parent_id = db.Column(db.Integer, db.ForeignKey("categoria.id"), nullable=True)
    subcategorias = db.relationship("Categoria", remote_side=[id])

# 🔹 Tabla de Transacciones
class Transaccion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(15), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categoria.id"), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.String(10), nullable=False)

# 🔹 Tabla de Presupuestos
class Presupuesto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categoria.id"), nullable=False)
    mes = db.Column(db.Integer, nullable=False)
    año = db.Column(db.Integer, nullable=False)
    monto_presupuestado = db.Column(db.Float, nullable=False)

# 🔹 Tabla de Resumen Mensual
class ResumenMensual(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mes = db.Column(db.Integer, nullable=False)
    año = db.Column(db.Integer, nullable=False)
    total_ingresos = db.Column(db.Float, default=0)
    total_gastos_fijos = db.Column(db.Float, default=0)
    total_gastos_variables = db.Column(db.Float, default=0)

# 🔹 CREAR LA BASE DE DATOS SI NO EXISTE
with app.app_context():
    db.create_all()
    print(f"✅ Base de datos creada en: {DB_PATH}")

# 🔹 Función para obtener los tipos únicos de transacciones desde la base de datos
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
        return ["ingreso", "gasto_fijo", "gasto_variable", "otro"]  # Valores predeterminados en caso de error

# 🔹 Función para obtener las categorías existentes y sus IDs
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