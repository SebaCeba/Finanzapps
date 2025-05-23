import os
import sqlite3
import pandas as pd
from flask import Flask, render_template
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px

# 🔹 Iniciar Flask
server = Flask(__name__)

# 🔹 Iniciar Dash dentro de Flask
app = dash.Dash(__name__, server=server, url_base_pathname="/editar-presupuesto/")

# 🔹 Ruta de la base de datos
DB_PATH = os.path.join(os.getcwd(), "instance", "finanzas.db")

# 🔹 Función para obtener datos de presupuesto
def obtener_presupuesto():
    conexion = sqlite3.connect(DB_PATH)
    query = """
    SELECT p.id, p.categoria_id, c.nombre as categoria, p.año, p.mes, p.monto_presupuestado
    FROM presupuesto p
    LEFT JOIN categoria c ON p.categoria_id = c.id
    """
    df = pd.read_sql_query(query, conexion)
    conexion.close()
    return df

# 🔹 Obtener datos iniciales
df = obtener_presupuesto()

# 🔹 Layout del Dashboard
app.layout = html.Div(style={"margin": "40px"}, children=[
    html.H1("📊 Editar Presupuesto"),
    html.Div(style={"display": "flex", "gap": "20px"}, children=[
        html.Div(children=[
            html.Label("Selecciona un Año:"),
            dcc.Dropdown(
                id="filtro-anio",
                options=[{"label": str(int(a)), "value": str(int(a))} for a in sorted(df['año'].unique()) if str(a).isdigit()],
                value=str(int(df['año'].max())),
                clearable=False,
                style={"width": "200px"}
            )
        ]),
        html.Div(children=[
            html.Label("Selecciona un Mes:"),
            dcc.Dropdown(
                id="filtro-mes",
                options=[
                    {"label": "Enero", "value": "01"},
                    {"label": "Febrero", "value": "02"},
                    {"label": "Marzo", "value": "03"},
                    {"label": "Abril", "value": "04"},
                    {"label": "Mayo", "value": "05"},
                    {"label": "Junio", "value": "06"},
                    {"label": "Julio", "value": "07"},
                    {"label": "Agosto", "value": "08"},
                    {"label": "Septiembre", "value": "09"},
                    {"label": "Octubre", "value": "10"},
                    {"label": "Noviembre", "value": "11"},
                    {"label": "Diciembre", "value": "12"},
                ],
                value="01",
                clearable=False,
                style={"width": "200px"}
            )
        ])
    ]),
    html.H2("Presupuesto Mensual"),
    html.Div(id="tabla-presupuesto"),
    html.Button("Guardar Cambios", id="guardar-cambios", n_clicks=0),
    html.Div(id="mensaje-guardado")
])

# 🔹 Callback para actualizar la tabla del presupuesto
@app.callback(
    Output("tabla-presupuesto", "children"),
    [Input("filtro-anio", "value"), Input("filtro-mes", "value")]
)
def actualizar_tabla(anio, mes):
    df_filtrado = df[(df['año'] == int(anio)) & (df['mes'] == int(mes))]
    return html.Table([
        html.Tr([html.Th("Categoría"), html.Th("Presupuesto"), html.Th("Nuevo Monto")]),
        *[html.Tr([
            html.Td(row["categoria"]),
            html.Td(f"${row['monto_presupuestado']:,.2f}"),
            html.Td(dcc.Input(id=f"input-{row['id']}", type="number", value=row['monto_presupuestado'], step="0.01"))
        ]) for _, row in df_filtrado.iterrows()]
    ])

# 🔹 Callback para guardar cambios en la base de datos
@app.callback(
    Output("mensaje-guardado", "children"),
    [Input("guardar-cambios", "n_clicks")],
    [State(f"input-{row['id']}", "value") for _, row in df.iterrows()]
)
def guardar_cambios(n_clicks, *valores):
    if n_clicks > 0:
        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()
        for (index, row), nuevo_monto in zip(df.iterrows(), valores):
            cursor.execute("UPDATE presupuesto SET monto_presupuestado = ? WHERE id = ?", (nuevo_monto, row['id']))
        conexion.commit()
        conexion.close()
        return "✅ Presupuesto actualizado con éxito!"
    return ""

# 🔹 Ejecutar Flask
if __name__ == "__main__":
    server.run(debug=True)