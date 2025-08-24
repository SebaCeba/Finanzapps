import sqlite3
import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog

# Crear una ventana emergente para seleccionar el archivo Excel
root = tk.Tk()
root.withdraw()  # Ocultar la ventana principal
file_path = filedialog.askopenfilename(title="Selecciona el archivo de categorías", filetypes=[("Archivos Excel", "*.xlsx")])

if not file_path:
    print("❌ No se seleccionó ningún archivo. Saliendo...")
    exit()

# Obtener la ruta absoluta de la base de datos dentro de 'instance/'
db_path = os.path.join(os.path.dirname(__file__), "instance", "finanzas.db")

# Conectar con la base de datos en 'instance/'
conexion = sqlite3.connect(db_path)
cursor = conexion.cursor()

# Cargar el archivo Excel
categorias_df = pd.read_excel(file_path)

# Convertir NaN en None para que SQLite lo reconozca como NULL
categorias_df = categorias_df.where(pd.notna(categorias_df), None)

# Insertar datos si no existen
for _, row in categorias_df.iterrows():
    cursor.execute("SELECT id FROM categoria WHERE nombre = ? AND tipo = ?", (row["nombre"], row["tipo"]))
    existe_categoria = cursor.fetchone()
    
    if not existe_categoria:
        cursor.execute("INSERT INTO categoria (id, nombre, tipo, parent_id) VALUES (?, ?, ?, ?)",
                       (row["id"], row["nombre"], row["tipo"], row["parent_id"]))

# Guardar y cerrar la conexión
conexion.commit()
conexion.close()

print("✅ Datos insertados correctamente en la base de datos")
