def obtener_presupuesto():
    conexion = sqlite3.connect(DB_PATH)
    query = """
    SELECT id, categoria_id, mes, año, monto_presupuestado
    FROM presupuesto
    """
    df = pd.read_sql_query(query, conexion)
    df.columns = df.columns.str.strip().str.lower()  # Normalizar nombres de columnas
    conexion.close()  # Asegurar que esté bien indentado
    return df

