import sqlite3

conexion = sqlite3.connect("finanzas.db")
cursor = conexion.cursor()

# Consultar categorías y subcategorías
cursor.execute("""
    SELECT c1.nombre AS categoria, c1.tipo, c2.nombre AS subcategoria
    FROM categorias c1
    LEFT JOIN categorias c2 ON c1.id = c2.parent_id
""")

resultados = cursor.fetchall()

print("📊 Categorías y Subcategorías Registradas:")
for categoria, tipo, subcategoria in resultados:
    sub = f" - {subcategoria}" if subcategoria else ""
    print(f"{categoria} ({tipo}){sub}")

conexion.close()