import os
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from app.models import db, Usuario

migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "auth.login"

def create_app():
    app = Flask(__name__)

    # ✅ Ruta segura para SQLite en Render (temporal)
    db_path = os.path.join("/tmp", "finanzas.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "super-secret-key"

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    from app.auth.routes import auth_bp
    from app.dashboard.routes import dashboard_bp
    from app.presupuesto.routes import presupuesto_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(presupuesto_bp)

    return app
