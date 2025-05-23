from flask import Flask, render_template
from database import db, Transaccion, ResumenMensual, Categoria

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///finanzas.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# 🔹 Página principal
@app.route("/")
def index():
    resumen = ResumenMensual.query.all()
    return render_template("index.html", resumen=resumen)

# 🔹 Página de transacciones
@app.route("/transacciones")
def transacciones():
    transacciones = Transaccion.query.all()
    return render_template("transacciones.html", transacciones=transacciones)

# 🔹 Página de categorías
@app.route("/categorias")
def mostrar_categorias():
    categorias = Categoria.query.filter_by(parent_id=None).all()
    subcategorias = Categoria.query.filter(Categoria.parent_id.isnot(None)).all()
    return render_template("categorias.html", categorias=categorias, subcategorias=subcategorias)

# 🔹 INTEGRAR DASH EN FLASK
import dash
from dash import dcc, html
import pandas as pd
import sqlite3
from dash.dependencies import Input, Output, State
import os

# Reusar app de Flask
dash_app = dash.Dash(__name__, server=app, url_base_pathname="/editar-presupuesto/")

# Conexión a base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), "instance", "finanzas.db")

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

df = obtener_presupuesto()

dash_app.layout = html.Div([
    html.H1("📊 Editar Presupuesto"),
    html.Div([
        html.Label("Año:"),
        dcc.Dropdown(
            id="filtro-anio",
            options=[{"label": str(int(a)), "value": str(int(a))} for a in sorted(df['año'].unique()) if str(a).isdigit()],
            value=str(int(df['año'].max()))
        ),
        html.Label("Mes:"),
        dcc.Dropdown(
            id="filtro-mes",
            options=[
                {"label": m, "value": str(i).zfill(2)}
                for i, m in enumerate(["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                                       "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], start=1)
            ],
            value="01"
        )
    ], style={"display": "flex", "gap": "20px"}),
    html.H2("Presupuesto Mensual"),
    html.Div(id="tabla-presupuesto"),
    html.Button("Guardar Cambios", id="guardar-cambios", n_clicks=0),
    html.Div(id="mensaje-guardado")
])

@dash_app.callback(
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

@dash_app.callback(
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



# 🔹 Ejecutar localmente
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)