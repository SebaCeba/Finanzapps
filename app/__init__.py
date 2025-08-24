# app/__init__.py
from flask import Flask, render_template
from flask_login import LoginManager, login_required
from app.extensions import db, migrate        # <- usa ESTE db
from app.dimensions import init_app as init_dimensions
from app.models import Usuario                # <- importa SOLO el modelo, no el db aquí
import os, secrets

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.secret_key = secrets.token_hex(16)

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, "..", "instance", "finanzas.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Inicializa extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    init_dimensions(app)                      # <- registra el API /api/...

    # Login
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Página de administración de dimensiones (UI)
    @app.get("/admin/dimensions")
    @login_required
    def admin_dimensions():
        return render_template("dimensions/index.html")

    # Blueprints existentes
    from app.auth.routes import auth_bp
    from app.dashboard.routes import dashboard_bp
    from app.presupuesto.routes import presupuesto_bp
    from app.real.routes import real_bp

    app.register_blueprint(presupuesto_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(real_bp)
    return app
