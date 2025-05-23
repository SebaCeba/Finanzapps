from flask import Flask, render_template, request, jsonify
import sqlite3
import json
import os
import requests
import dash
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc

# 🔹 Ruta de la base de datos
DB_PATH = os.path.join(os.getcwd(), "instance", "finanzas.db")

app = Flask(__name__)
dash_app = Dash(__name__, server=app, url_base_pathname='/dash/', external_stylesheets=[dbc.themes.BOOTSTRAP])

# 🔹 Función para obtener categorías desde SQLite en formato de árbol
def obtener_categorias():
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre, tipo, parent_id FROM categoria")
    categories = cursor.fetchall()
    conexion.close()
    
    category_dict = {str(cat[0]): {"label": cat[1], "value": str(cat[0]), "children": []} for cat in categories}
    tree = []
    
    for cat in categories:
        if cat[3] is not None and str(cat[3]) in category_dict:
            category_dict[str(cat[3])]["children"].append(category_dict[str(cat[0])])
        else:
            tree.append(category_dict[str(cat[0])])
    
    return tree

dash_app.layout = dbc.Container([
    html.H1("Gestión de Categorías", className="text-center mt-3 mb-4"),
    dbc.Row([
        dbc.Col([
            html.Label("Nombre de Categoría:"),
            dcc.Input(id="input-nombre", type="text", placeholder="Nuevo nombre", className="form-control mb-2"),
            html.Label("Selecciona nuevo padre:"),
            dcc.Dropdown(id="dropdown-parent", placeholder="Selecciona nuevo padre", className="mb-2"),
            dbc.Button("Guardar Cambios", id="save-button", color="primary", className="w-100 mb-2"),
            dbc.Button("Agregar Nodo", id="add-button", color="success", className="w-100 mb-2"),
            dbc.Button("Eliminar Nodo", id="delete-button", color="danger", className="w-100"),
        ], width=4),
        dbc.Col([
            dcc.Store(id="selected-node"),
            html.Div(id="categoria-tree", style={'border': '1px solid #ddd', 'border-radius': '5px', 'padding': '10px'})
        ], width=8)
    ])
], fluid=True)

@dash_app.callback(
    [Output('categoria-tree', 'children'), Output('dropdown-parent', 'options')],
    Input('selected-node', 'data')
)
def update_tree(_):
    categorias = obtener_categorias()
    opciones_parent = [{'label': 'Ninguno', 'value': None}] + [{'label': cat['label'], 'value': cat['value']} for cat in categorias]
    
    def generar_lista(categorias):
        return html.Ul([
            html.Li([
                html.Span(cat['label'], style={'font-weight': 'bold', 'cursor': 'pointer'}),
                generar_lista(cat['children']) if cat['children'] else None
            ]) for cat in categorias
        ])
    
    return generar_lista(categorias), opciones_parent

if __name__ == "__main__":
    app.run(debug=True)
