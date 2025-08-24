import click
from flask.cli import with_appcontext
from .routes import bp as dimensions_bp

def init_app(app):
    # Registra el blueprint de la API (si existe)
    try:
        app.register_blueprint(dimensions_bp)
    except Exception:
        pass

    # ✅ Comando CLI: flask seed-dimensions
    @app.cli.command("seed-dimensions")
    @with_appcontext
    def seed_dimensions_cmd():
        """Carga dimensiones base (ACCOUNT, ENTITY, COSTCENTER, SCENARIO, TIME)."""
        from .seed import seed_dimensions  # tu función existente
        seed_dimensions()
        click.echo("Seed OK")