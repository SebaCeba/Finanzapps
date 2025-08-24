import sqlite3
import os
import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# 🔹 Ruta de la base de datos
DB_PATH = os.path.join(os.getcwd(), "instance", "finanzas.db")

# 🔹 Función para verificar y crear la tabla si no existe
def verificar_bd():
    if not os.path.exists(os.path.dirname(DB_PATH)):
        os.makedirs(os.path.dirname(DB_PATH))
    
    with sqlite3.connect(DB_PATH) as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS categoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL
        )""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS presupuesto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria_id INTEGER,
            año INTEGER,
            mes INTEGER,
            monto_presupuestado REAL,
            FOREIGN KEY (categoria_id) REFERENCES categoria(id)
        )""")
        conexion.commit()

# 🔹 Función para obtener categorías desde la base de datos
def obtener_categorias_desde_bd():
    try:
        with sqlite3.connect(DB_PATH) as conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT id, nombre FROM categoria ORDER BY nombre")
            return {nombre: id for id, nombre in cursor.fetchall()}
    except Exception as e:
        print(f"❌ Error al obtener categorías: {e}")
        return {}

# 🔹 Función para cargar presupuestos desde un archivo
def seleccionar_archivo():
    file_path = filedialog.askopenfilename(
        title="Selecciona un archivo de presupuesto",
        filetypes=[("Archivos CSV", "*.csv"), ("Archivos Excel", "*.xlsx")]
    )

    if not file_path:
        return

    try:
        presupuesto_df = pd.read_excel(file_path, engine="openpyxl") if file_path.endswith(".xlsx") else pd.read_csv(file_path)
        
        columnas_esperadas = {"categoria_id", "año", "mes", "monto_presupuestado"}
        if not columnas_esperadas.issubset(presupuesto_df.columns):
            messagebox.showerror("Error", f"El archivo debe contener las columnas: {columnas_esperadas}")
            return

        with sqlite3.connect(DB_PATH) as conexion:
            cursor = conexion.cursor()
            cursor.executemany(
                "INSERT INTO presupuesto (categoria_id, año, mes, monto_presupuestado) VALUES (?, ?, ?, ?)",
                presupuesto_df[["categoria_id", "año", "mes", "monto_presupuestado"]].values.tolist()
            )
            conexion.commit()

        messagebox.showinfo("Éxito", "Presupuestos cargados correctamente.")
    
    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron cargar los presupuestos: {e}")

# 🔹 Inicializar la BD antes de continuar
verificar_bd()

# 🔹 Crear la ventana principal
root = tk.Tk()
root.withdraw()  # Ocultar la ventana principal mientras se selecciona el archivo

# 🔹 Abrir el Pop-up de selección de archivo automáticamente
seleccionar_archivo()

# 🔹 Mostrar la ventana principal
root.deiconify()
root.title("Añadir Presupuesto")
root.geometry("400x300")
root.resizable(False, False)

# 🔹 Obtener categorías
categorias_dict = obtener_categorias_desde_bd()
nombres_categorias = [""] + list(categorias_dict.keys())

# 🔹 Crear los campos de entrada
tk.Label(root, text="Categoría:").pack(pady=5)
combo_categoria = ttk.Combobox(root, values=nombres_categorias, width=37)
combo_categoria.pack(pady=5)

tk.Label(root, text="Año:").pack(pady=5)
entry_año = tk.Entry(root, width=40)
entry_año.pack(pady=5)

tk.Label(root, text="Mes:").pack(pady=5)
entry_mes = tk.Entry(root, width=40)
entry_mes.pack(pady=5)

tk.Label(root, text="Monto Presupuestado:").pack(pady=5)
entry_monto = tk.Entry(root, width=40)
entry_monto.pack(pady=5)

# 🔹 Validación de entradas numé
