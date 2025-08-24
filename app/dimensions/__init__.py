import click
from flask.cli import with_appcontext

# Si ya tienes un blueprint de API en routes.py, lo importamos
try:
    from .routes import bp as dimensions_bp
except Exception:
    dimensions_bp = None

def init_app(app):
    # Registrar API si existe
    if dimensions_bp:
        app.register_blueprint(dimensions_bp)

    # Comando CLI para seed
    @app.cli.command("seed-dimensions")
    @with_appcontext
    def seed_dimensions_cmd():
        """Carga dimensiones base (ACCOUNT, ENTITY, COSTCENTER, SCENARIO, TIME)."""
        from .seed import seed_dimensions
        seed_dimensions()
        click.echo("Seed OK")
