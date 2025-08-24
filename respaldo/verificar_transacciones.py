import sqlite3
import os

# 🔹 Ruta de la base de datos
DB_PATH = os.path.join(os.getcwd(), "instance", "finanzas.db")

# 🔹 Conectar con la base de datos
conexion = sqlite3.connect(DB_PATH)
cursor = conexion.cursor()

# 🔹 Consultar todas las transacciones
cursor.execute("SELECT id, fecha, tipo, categoria_id, monto FROM transaccion ORDER BY fecha;")
transacciones = cursor.fetchall()

# 🔹 Mostrar transacciones en consola
print("\n📊 **TRANSACCIONES REGISTRADAS:**\n")
for id, fecha, tipo, categoria_id, monto in transacciones:
    print(f"ID: {id} | Fecha: {fecha} | Tipo: {tipo} | Categoría ID: {categoria_id} | Monto: {monto}")

# 🔹 Cerrar conexión
conexion.close()
