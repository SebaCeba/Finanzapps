import sqlite3
import os

# 🔹 Ruta de la base de datos
DB_PATH = os.path.join(os.getcwd(), "instance", "finanzas.db")

# 🔹 Verificar que la base de datos existe
if not os.path.exists(DB_PATH):
    print(f"❌ La base de datos no existe en: {DB_PATH}. Ejecuta database.py primero.")
    exit(1)

# 🔹 Conectar a la base de datos
conexion = sqlite3.connect(DB_PATH)
cursor = conexion.cursor()

# 🔹 Consultar las categorías
cursor.execute("SELECT id, nombre, tipo, parent_id FROM categoria ORDER BY id;")
categorias = cursor.fetchall()

# 🔹 Mostrar las categorías en consola
print("\n📊 **CATEGORÍAS REGISTRADAS EN LA BASE DE DATOS:**\n")
for id, nombre, tipo, parent_id in categorias:
    print(f"ID: {id} | Nombre: {nombre} | Tipo: {tipo} | Parent ID: {parent_id}")

# 🔹 Cerrar conexión
conexion.close()
