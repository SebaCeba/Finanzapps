import sqlite3
import pandas as pd

DB_PATH = "instance/finanzas.db"

def obtener_presupuesto_anual(año):
    conexion = sqlite3.connect(DB_PATH)
    query = """
    SELECT p.categoria_id, c.nombre as categoria, p.año, p.mes, p.monto_presupuestado
    FROM presupuesto p
    LEFT JOIN categoria c ON p.categoria_id = c.id
    WHERE p.año = ?
    ORDER BY c.nombre, p.mes
    """
    df = pd.read_sql_query(query, conexion, params=(año,))
    conexion.close()
    return df

df = obtener_presupuesto_anual(2025)
print(df)
