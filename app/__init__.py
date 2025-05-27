from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate  # ✅ IMPORTAR
from app.models import db, Usuario

migrate = Migrate()  # ✅ Instancia global
login_manager = LoginManager()
login_manager.login_view = "auth.login"

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    migrate.init_app(app, db)  # ✅ ESTA LÍNEA FALTABA
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
