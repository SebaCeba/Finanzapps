import os
import sqlite3
import pandas as pd
from flask import Flask
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ALL
import plotly.express as px

# 🔹 Iniciar Flask
server = Flask(__name__)

# 🔹 Iniciar Dash dentro de Flask
app = dash.Dash(__name__, server=server, url_base_pathname="/panel/")

# 🔹 Ruta de la base de datos
DB_PATH = os.path.join(os.getcwd(), "instance", "finanzas.db")

# 🔹 Función para obtener datos filtrados
def obtener_datos(anio=None, mes=None):
    conexion = sqlite3.connect(DB_PATH)
    query = """
    SELECT c.id as categoria_id, c.nombre as categoria, c.tipo, c.parent_id,
           COALESCE(SUM(t.monto), 0) as monto, 
           COALESCE(p.monto_presupuestado, 0) as monto_presupuestado
    FROM categoria c
    LEFT JOIN transaccion t ON c.id = t.categoria_id 
        AND strftime('%Y', t.fecha) = ? 
        AND strftime('%m', t.fecha) = ?
    LEFT JOIN presupuesto p ON c.id = p.categoria_id 
        AND p.año = ? 
        AND p.mes = ?
    WHERE c.parent_id IS NOT NULL
    GROUP BY c.id, c.nombre, c.tipo, c.parent_id, p.monto_presupuestado
    """
    
    df = pd.read_sql_query(query, conexion, params=(anio, mes, anio, mes))
    conexion.close()
    
    return df

# 🔹 Obtener años disponibles
def obtener_anios():
    conexion = sqlite3.connect(DB_PATH)
    query = "SELECT DISTINCT strftime('%Y', fecha) as anio FROM transaccion ORDER BY anio DESC"
    anios = pd.read_sql_query(query, conexion)["anio"].tolist()
    conexion.close()
    return anios

# 🔹 Obtener lista de años solo una vez
anios_disponibles = obtener_anios()

# 🔹 Layout del Dashboard
app.layout = html.Div(style={"margin": "40px"}, children=[
    html.H1("📊 Panel de Control Financiero"),

    html.Div(style={"display": "flex", "gap": "20px"}, children=[
        html.Div(children=[
            html.Label("Selecciona un Año:"),
            dcc.Dropdown(
                id="filtro-anio",
                options=[{"label": str(a), "value": str(a)} for a in anios_disponibles],
                value=anios_disponibles[0] if anios_disponibles else None,
                clearable=False,
                style={"width": "200px"}
            )
        ]),
        html.Div(children=[
            html.Label("Selecciona un Mes:"),
            dcc.Dropdown(
                id="filtro-mes",
                options=[{"label": mes, "value": f"{idx:02d}"} for idx, mes in enumerate([
                    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], start=1)],
                value="01",
                clearable=False,
                style={"width": "200px"}
            )
        ])
    ]),

    html.Div(style={"display": "flex", "justify-content": "space-between", "align-items": "start", "margin-top": "20px"}, children=[
        html.Div(style={"width": "40%"}, children=[
            html.H2("Resumen Financiero"),
            html.Div(id="resumen-categoria")
        ]),
        html.Div(style={"width": "55%"}, children=[
            dcc.Graph(id="grafico-ingresos-gastos")
        ])
    ]),

    html.Button("Guardar Cambios", id="guardar-cambios", n_clicks=0, style={"margin-top": "20px"}),
    html.Div(id="mensaje-guardado", style={"margin-top": "10px", "fontWeight": "bold"})
])

# 🔹 Callback para actualizar el panel y permitir edición en "Registro Financiero"
@app.callback(
    [Output("resumen-categoria", "children"),
     Output("grafico-ingresos-gastos", "figure")],
    [Input("filtro-anio", "value"), Input("filtro-mes", "value")]
)
def actualizar_panel(anio, mes):
    df_filtrado = obtener_datos(anio, mes)

    if df_filtrado.empty:
        return html.P("No hay datos disponibles para este período.", style={"fontSize": "18px"}), px.bar(title="Sin datos disponibles")

    df_filtrado["variacion"] = df_filtrado["monto_presupuestado"] - df_filtrado["monto"]

    tabla = html.Table([
        html.Tr([
            html.Th("Categoría", style={"text-align": "center", "padding": "3px", "width": "30%", "vertical-align": "middle", "height": "30px"}),
            html.Th("Registro Financiero", style={"text-align": "center", "padding": "3px", "width": "20%", "vertical-align": "middle", "height": "30px"}),
            html.Th("Presupuesto", style={"text-align": "center", "padding": "3px", "width": "20%", "vertical-align": "middle", "height": "30px"}),
            html.Th("Variación del Presupuesto", style={"text-align": "center", "padding": "3px", "width": "20%", "vertical-align": "middle", "height": "30px"})
        ])
    ] + [
        html.Tr([
            html.Td(row["categoria"], style={"text-align": "left", "padding": "3px", "vertical-align": "middle", "height": "30px"}),
            html.Td(dcc.Input(
                id={"type": "input-registro-financiero", "index": row["categoria_id"]},
                type="text",
                value=f"{row['monto']:,.0f}".replace(",", "."),
                style={"width": "100%", "text-align": "right", "vertical-align": "middle"}
            )),
            html.Td(f"{row['monto_presupuestado']:,.0f}".replace(",", "."), style={"text-align": "right", "padding": "3px", "vertical-align": "middle"}),
            html.Td(f"{row['variacion']:,.0f}".replace(",", "."), style={"text-align": "right", "padding": "3px", "vertical-align": "middle"})
        ]) for _, row in df_filtrado.iterrows()
    ])

    fig = px.bar(df_filtrado, x='categoria', y='monto', color='tipo', title="Ingresos y Gastos por Categoría")

    return tabla, fig

# 🔹 Callback para guardar cambios en "Registro Financiero"
@app.callback(
    Output("mensaje-guardado", "children"),
    [Input("guardar-cambios", "n_clicks")],
    [State("filtro-anio", "value"), State("filtro-mes", "value"),
     State({"type": "input-registro-financiero", "index": ALL}, "value"),
     State({"type": "input-registro-financiero", "index": ALL}, "id")]
)
def guardar_cambios(n_clicks, anio, mes, valores, ids):
    if n_clicks > 0:
        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()

        for i, categoria_id in enumerate(ids):
            nuevo_monto = float(valores[i].replace(".", "")) if valores[i] else 0
            categoria_id = categoria_id["index"]

            # 🔹 Verificar si el registro existe
            cursor.execute("""
                SELECT COUNT(*) FROM transaccion WHERE categoria_id = ? AND strftime('%Y', fecha) = ? AND strftime('%m', fecha) = ?
            """, (categoria_id, anio, mes))
            existe = cursor.fetchone()[0]

            if existe:
                # 🔹 Si existe, hacer UPDATE
                cursor.execute("""
                    UPDATE transaccion SET monto = ? 
                    WHERE categoria_id = ? AND strftime('%Y', fecha) = ? AND strftime('%m', fecha) = ?
                """, (nuevo_monto, categoria_id, anio, mes))
            else:
                # 🔹 Si no existe, hacer INSERT
                cursor.execute("""
                    INSERT INTO transaccion (categoria_id, monto, fecha, tipo) 
                    VALUES (?, ?, ?, 'gasto_variable')
                """, (categoria_id, nuevo_monto, f"{anio}-{mes}-01"))

        conexion.commit()
        conexion.close()
        return "✅ Cambios guardados correctamente."

    return ""

# 🔹 Ejecutar Flask
if __name__ == "__main__":
    server.run(debug=True)
