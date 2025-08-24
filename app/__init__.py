from flask import Flask
from flask_login import LoginManager
from app.extensions import db, migrate
from app.dimensions import init_app as init_dimensions
import os, secrets

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.secret_key = secrets.token_hex(16)

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, "..", "instance", "finanzas.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Extensiones
    db.init_app(app)
    migrate.init_app(app, db)

    # Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id: str):
        # import interno para evitar ciclos
        from app.models import Usuario
        try:
            return db.session.get(Usuario, int(user_id))  # SQLAlchemy 2.x
        except Exception:
            return None

    # Blueprints existentes de tu app
    from app.auth.routes import auth_bp
    from app.dashboard.routes import dashboard_bp
    from app.presupuesto.routes import presupuesto_bp
    from app.real.routes import real_bp

    app.register_blueprint(presupuesto_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(real_bp)

    # ✅ UI de dimensiones
    from app.admin.routes import admin_bp
    app.register_blueprint(admin_bp)

    # ✅ API de dimensiones (+ comando seed)
    init_dimensions(app)

    # ✅ API de hechos (coma decimal)
    from app.facts.routes import facts_bp
    app.register_blueprint(facts_bp)

    return app
