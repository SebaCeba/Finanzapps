import os
from flask import Flask, render_template
import dash
from dash import dcc, html, Input, Output, State, ctx
import dash_cytoscape as cyto
import sqlite3

# 🔹 Ruta de la base de datos
DB_PATH = os.path.join(os.getcwd(), "instance", "finanzas.db")

# 🔹 Función para obtener categorías desde SQLite
def obtener_categorias():
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre, tipo, parent_id FROM categoria")
    categorias = cursor.fetchall()
    conexion.close()

    nodos = []
    edges = []
    for cat in categorias:
        nodos.append({"data": {"id": str(cat[0]), "label": cat[1]}})
        if cat[3]:  # Si tiene parent_id
            edges.append({"data": {"source": str(cat[3]), "target": str(cat[0])}})

    return nodos + edges

# 🔹 Inicializar Flask
app = Flask(__name__)

# 🔹 Inicializar Dash dentro de Flask
dash_app = dash.Dash(
    __name__,
    server=app,
    url_base_pathname="/editar-categorias/",
    suppress_callback_exceptions=True
)

# 🔹 Layout de Dash para la edición de categorías
dash_app.layout = html.Div([
    html.H2("Gestión de Categorías"),
    cyto.Cytoscape(
        id="arbol-categorias",
        elements=obtener_categorias(),
        layout={"name": "breadthfirst"},
        style={"width": "100%", "height": "500px"},
        stylesheet=[
            {"selector": "node", "style": {"label": "data(label)", "background-color": "#1E88E5", "color": "white"}},
            {"selector": "edge", "style": {"curve-style": "bezier", "target-arrow-shape": "triangle"}}
        ],
    ),
    html.Div([
        html.Button("Agregar Categoría", id="btn-agregar", n_clicks=0),
        html.Button("Eliminar Categoría", id="btn-eliminar", n_clicks=0),
        html.Button("Editar Nombre", id="btn-editar", n_clicks=0),
        html.Button("Guardar Cambios", id="btn-guardar", n_clicks=0),
    ], style={"margin-bottom": "10px"}),
    
    dcc.Input(id="input-nombre", type="text", placeholder="Nombre de la categoría", style={"display": "none"}),
    html.Div(id="mensaje"),
])

# 🔹 Callback para seleccionar un nodo
@dash_app.callback(
    Output("input-nombre", "value"),
    Output("input-nombre", "style"),
    Input("arbol-categorias", "tapNodeData"),
    prevent_initial_call=True
)
def seleccionar_categoria(nodo):
    if nodo:
        return nodo["label"], {"display": "inline-block", "margin-left": "10px"}
    return "", {"display": "none"}

# 🔹 Callback para agregar una categoría
@dash_app.callback(
    Output("mensaje", "children"),
    Output("arbol-categorias", "elements"),
    Input("btn-agregar", "n_clicks"),
    State("input-nombre", "value"),
    State("arbol-categorias", "tapNodeData"),
    prevent_initial_call=True
)
def agregar_categoria(n_clicks, nombre, nodo_padre):
    if not nombre:
        return "Por favor, ingresa un nombre.", obtener_categorias()

    parent_id = nodo_padre["id"] if nodo_padre else None

    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO categoria (nombre, tipo, parent_id) VALUES (?, 'gasto_variable', ?)", (nombre, parent_id))
    conexion.commit()
    conexion.close()

    return f"Categoría '{nombre}' agregada con éxito.", obtener_categorias()

# 🔹 Callback para eliminar una categoría
@dash_app.callback(
    Output("mensaje", "children"),
    Output("arbol-categorias", "elements"),
    Input("btn-eliminar", "n_clicks"),
    State("arbol-categorias", "tapNodeData"),
    prevent_initial_call=True
)
def eliminar_categoria(n_clicks, nodo):
    if not nodo:
        return "Selecciona una categoría para eliminar.", obtener_categorias()

    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM categoria WHERE id=?", (nodo["id"],))
    conexion.commit()
    conexion.close()

    return f"Categoría '{nodo['label']}' eliminada.", obtener_categorias()

# 🔹 Callback para editar el nombre de una categoría
@dash_app.callback(
    Output("mensaje", "children"),
    Output("arbol-categorias", "elements"),
    Input("btn-editar", "n_clicks"),
    State("arbol-categorias", "tapNodeData"),
    State("input-nombre", "value"),
    prevent_initial_call=True
)
def editar_categoria(n_clicks, nodo, nuevo_nombre):
    if not nodo or not nuevo_nombre:
        return "Selecciona una categoría y un nuevo nombre.", obtener_categorias()

    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    cursor.execute("UPDATE categoria SET nombre=? WHERE id=?", (nuevo_nombre, nodo["id"]))
    conexion.commit()
    conexion.close()

    return f"Nombre cambiado a '{nuevo_nombre}'.", obtener_categorias()

# 🔹 Callback para guardar cambios en la jerarquía
@dash_app.callback(
    Output("mensaje", "children"),
    Output("arbol-categorias", "elements"),
    Input("btn-guardar", "n_clicks"),
    State("arbol-categorias", "elements"),
    prevent_initial_call=True
)
def guardar_cambios(n_clicks, elementos):
    if not elementos:
        return "No hay cambios para guardar.", obtener_categorias()

    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()

    for elem in elementos:
        if "source" in elem["data"] and "target" in elem["data"]:
            categoria_id = elem["data"]["target"]
            nuevo_parent_id = elem["data"]["source"]
            cursor.execute("UPDATE categoria SET parent_id=? WHERE id=?", (nuevo_parent_id, categoria_id))

    conexion.commit()
    conexion.close()

    return "Cambios guardados con éxito.", obtener_categorias()

# 🔹 Ruta principal en Flask
@app.route("/")
def index():
    return "<h1>Bienvenido a la Webapp de Finanzas</h1><p>Ir a <a href='/editar-categorias/'>Edición de Categorías</a></p>"

# 🔹 Ejecutar la aplicación Flask
if __name__ == "__main__":
    app.run(debug=True)
