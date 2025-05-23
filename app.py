from flask import Flask, render_template
from database import db, Transaccion, ResumenMensual

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///finanzas.db"
db.init_app(app)

@app.route("/")
def index():
    resumen = ResumenMensual.query.all()
    return render_template("index.html", resumen=resumen)

@app.route("/transacciones")
def transacciones():
    transacciones = Transaccion.query.all()
    return render_template("transacciones.html", transacciones=transacciones)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
from flask import render_template

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/categorias")
def mostrar_categorias():
    categorias = Categoria.query.filter_by(parent_id=None).all()
    subcategorias = Categoria.query.filter(Categoria.parent_id.isnot(None)).all()
    return render_template("categorias.html", categorias=categorias, subcategorias=subcategorias)

@app.route("/transacciones")
def transacciones():
    return "<h1>Página de transacciones (en construcción)</h1>"

