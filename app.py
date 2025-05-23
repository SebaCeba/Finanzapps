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

# INTEGRAR DASH EN FLASK
import dash
from dash import dcc, html
import pandas as pd
import sqlite3
import os
from dash.dependencies import Input, Output, State, MATCH, ALL

# Reusar app de Flask
dash_app = dash.Dash(__name__, server=app, url_base_pathname="/editar-presupuesto/", suppress_callback_exceptions=True)

# Ruta base a la base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), "instance", "finanzas.db")

# Función para obtener presupuesto actualizado
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

# Layout
dash_app.layout = html.Div([
    html.H1("📊 Editar Presupuesto"),
    
    html.Div([
        html.Label("Año:"),
        dcc.Dropdown(id="filtro-anio"),
        
        html.Label("Mes:"),
        dcc.Dropdown(
            id="filtro-mes",
            options=[
                {"label": m, "value": i}
                for i, m in enumerate(["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                                       "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], start=1)
            ],
            value=1
        )
    ], style={"display": "flex", "gap": "20px", "marginBottom": "20px"}),

    html.H2("Presupuesto Mensual"),
    html.Div(id="tabla-presupuesto"),

    html.Button("Guardar Cambios", id="guardar-cambios", n_clicks=0),
    html.Div(id="mensaje-guardado", style={"marginTop": "10px", "color": "green"})
])

# Callback para llenar opciones de año
@dash_app.callback(
    Output("filtro-anio", "options"),
    Output("filtro-anio", "value"),
    Input("filtro-mes", "value")  # se dispara al cargar también
)
def actualizar_opciones_anio(_):
    df = obtener_presupuesto()
    opciones = [{"label": str(int(a)), "value": int(a)} for a in sorted(df['año'].unique())]
    valor_default = opciones[-1]["value"] if opciones else None
    return opciones, valor_default

# Callback para generar la tabla con inputs
@dash_app.callback(
    Output("tabla-presupuesto", "children"),
    [Input("filtro-anio", "value"), Input("filtro-mes", "value")]
)
def actualizar_tabla(anio, mes):
    df = obtener_presupuesto()
    df_filtrado = df[(df["año"] == int(anio)) & (df["mes"] == int(mes))]

    if df_filtrado.empty:
        return html.P("⚠️ No hay presupuestos definidos para este mes y año.")

    tabla = [
        html.Tr([html.Th("Categoría"), html.Th("Presupuesto Actual"), html.Th("Nuevo Monto")])
    ]

    for _, row in df_filtrado.iterrows():
        tabla.append(html.Tr([
            html.Td(row["categoria"]),
            html.Td(f"${row['monto_presupuestado']:,.2f}"),
            html.Td(dcc.Input(
                id={"type": "input-presupuesto", "index": row["id"]},
                type="number",
                value=row["monto_presupuestado"],
                step="0.01"
            ))
        ]))

    return html.Table(tabla, style={"width": "100%", "borderCollapse": "collapse"})

# Callback para guardar los cambios
@dash_app.callback(
    Output("mensaje-guardado", "children"),
    Input("guardar-cambios", "n_clicks"),
    State("filtro-anio", "value"),
    State("filtro-mes", "value"),
    State({"type": "input-presupuesto", "index": ALL}, "value"),
    State({"type": "input-presupuesto", "index": ALL}, "id")
)
def guardar_cambios(n_clicks, anio, mes, valores, ids):
    if n_clicks == 0:
        return ""

    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()

    for nuevo_monto, input_id in zip(valores, ids):
        presupuesto_id = input_id["index"]
        cursor.execute("UPDATE presupuesto SET monto_presupuestado = ? WHERE id = ?", (nuevo_monto, presupuesto_id))

    conexion.commit()
    conexion.close()

    return "✅ Presupuesto actualizado con éxito."



# 🔹 Ejecutar localmente
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)