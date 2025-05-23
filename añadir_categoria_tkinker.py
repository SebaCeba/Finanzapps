import sqlite3
import os
import tkinter as tk
from tkinter import ttk, messagebox

# 🔹 Ruta de la base de datos
DB_PATH = os.path.join(os.getcwd(), "instance", "finanzas.db")

# 🔹 Función para obtener los tipos únicos de la base de datos
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

# 🔹 Función para insertar la categoría en la base de datos
def insertar_categoria():
    nombre = entry_nombre.get().strip()
    tipo = combo_tipo.get().strip().lower()  # Ahora puede aceptar valores personalizados
    parent_id = entry_parent_id.get().strip()

    # Validaciones básicas
    if not nombre:
        messagebox.showerror("Error", "El nombre de la categoría no puede estar vacío.")
        return
    
    if not tipo:
        messagebox.showerror("Error", "El tipo de categoría no puede estar vacío.")
        return

    parent_id = int(parent_id) if parent_id.isdigit() else None  # Convertir a int si es un número

    try:
        # Conectar a la base de datos
        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()

        # Insertar en la base de datos
        cursor.execute(
            "INSERT INTO categoria (nombre, tipo, parent_id) VALUES (?, ?, ?)",
            (nombre, tipo, parent_id),
        )
        conexion.commit()
        conexion.close()

        # Mostrar mensaje de éxito y limpiar los campos
        messagebox.showinfo("Éxito", f"Categoría '{nombre}' añadida correctamente con tipo '{tipo}'.")
        entry_nombre.delete(0, tk.END)
        combo_tipo.set("")
        entry_parent_id.delete(0, tk.END)

        # 🔹 Actualizar los valores del ComboBox después de agregar un nuevo tipo
        actualizar_combobox()

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo insertar la categoría: {e}")

# 🔹 Función para actualizar el ComboBox con los nuevos tipos de la base de datos
def actualizar_combobox():
    tipos_actualizados = obtener_tipos_desde_bd()
    combo_tipo["values"] = tipos_actualizados  # 🔥 Actualiza la lista del ComboBox

# 🔹 Crear la ventana principal
root = tk.Tk()
root.title("Añadir Categoría")
root.geometry("350x250")
root.resizable(False, False)

# 🔹 Crear los campos de entrada
tk.Label(root, text="Nombre de la Categoría:").pack(pady=5)
entry_nombre = tk.Entry(root, width=30)
entry_nombre.pack(pady=5)

tk.Label(root, text="Tipo de Categoría:").pack(pady=5)

# 🔹 Inicializar ComboBox con los tipos desde la base de datos
tipos_iniciales = obtener_tipos_desde_bd()
combo_tipo = ttk.Combobox(root, values=tipos_iniciales, width=27)
combo_tipo.pack(pady=5)
combo_tipo.set("")

tk.Label(root, text="ID de la Categoría Padre (Opcional):").pack(pady=5)
entry_parent_id = tk.Entry(root, width=30)
entry_parent_id.pack(pady=5)

# 🔹 Botón para añadir la categoría
btn_añadir = tk.Button(root, text="Añadir Categoría", command=insertar_categoria)
btn_añadir.pack(pady=20)

# 🔹 Ejecutar la ventana
root.mainloop()
