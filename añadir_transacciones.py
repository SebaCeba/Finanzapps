import sqlite3
import os
import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# 🔹 Ruta de la base de datos
DB_PATH = os.path.join(os.getcwd(), "instance", "finanzas.db")

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

# 🔹 Función para seleccionar un archivo y cargar transacciones en la base de datos
def seleccionar_archivo():
    file_path = filedialog.askopenfilename(
        title="Selecciona un archivo de transacciones",
        filetypes=[("Archivos CSV", "*.csv"), ("Archivos Excel", "*.xlsx")]
    )

    if not file_path:
        return  # No hacer nada si el usuario cancela la selección

    try:
        if file_path.endswith(".xlsx"):
            transacciones_df = pd.read_excel(file_path, engine="openpyxl")
        elif file_path.endswith(".csv"):
            transacciones_df = pd.read_csv(file_path)
        else:
            messagebox.showerror("Error", "Formato de archivo no válido.")
            return

        columnas_esperadas = {"fecha", "tipo", "categoria_id", "monto"}
        if not columnas_esperadas.issubset(transacciones_df.columns):
            messagebox.showerror("Error", f"El archivo debe contener las columnas: {columnas_esperadas}")
            return

        # 🔹 Convertir fecha a string en formato 'YYYY-MM-DD'
        transacciones_df["fecha"] = pd.to_datetime(transacciones_df["fecha"], errors='coerce').dt.strftime('%Y-%m-%d')

        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()

        for _, row in transacciones_df.iterrows():
            cursor.execute(
                "INSERT INTO transaccion (fecha, tipo, categoria_id, monto) VALUES (?, ?, ?, ?)",
                (row["fecha"], row["tipo"], row["categoria_id"], row["monto"]),
            )

        conexion.commit()
        conexion.close()

        messagebox.showinfo("Éxito", "Las transacciones fueron cargadas correctamente.")

    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron cargar las transacciones: {e}")

# 🔹 Crear la ventana principal
root = tk.Tk()
root.withdraw()  # Ocultar la ventana principal mientras se selecciona el archivo

# 🔹 Abrir el Pop-up de selección de archivo automáticamente
seleccionar_archivo()

# 🔹 Mostrar la ventana para ingreso manual si el usuario cancela la selección
root.deiconify()
root.title("Añadir Transacción")
root.geometry("400x350")
root.resizable(False, False)

# 🔹 Crear los campos de entrada
tk.Label(root, text="Fecha (YYYY-MM-DD):").pack(pady=5)
entry_fecha = tk.Entry(root, width=40)
entry_fecha.pack(pady=5)

tk.Label(root, text="Tipo de Transacción:").pack(pady=5)
tipos_iniciales = obtener_tipos_desde_bd()
combo_tipo = ttk.Combobox(root, values=tipos_iniciales, width=37)
combo_tipo.pack(pady=5)
combo_tipo.set("")

tk.Label(root, text="Categoría:").pack(pady=5)
lista_categorias = obtener_categorias_desde_bd()
nombres_categorias = [nombre for _, nombre in lista_categorias]
combo_categoria = ttk.Combobox(root, values=[""] + nombres_categorias, width=37)
combo_categoria.pack(pady=5)
combo_categoria.set("")

tk.Label(root, text="Monto:").pack(pady=5)
entry_monto = tk.Entry(root, width=40)
entry_monto.pack(pady=5)

# 🔹 Botón para añadir transacción manualmente
btn_añadir = tk.Button(root, text="Añadir Transacción", command=insertar_transaccion)
btn_añadir.pack(pady=10)

# 🔹 Ejecutar la ventana
root.mainloop()