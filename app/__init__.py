# app/__init__.py

from flask import Flask
from flask_login import LoginManager
from app.models import db, Usuario
import os, secrets

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.secret_key = secrets.token_hex(16)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, "..", "instance", "finanzas.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    with app.app_context():
        db.create_all()

    # 👇 registra aquí tus blueprints
    from app.auth.routes import auth_bp
    from app.dashboard.routes import dashboard_bp
    from app.presupuesto.routes import presupuesto_bp
    app.register_blueprint(presupuesto_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    return app
