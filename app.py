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

# 🔹 Ejecutar localmente
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)