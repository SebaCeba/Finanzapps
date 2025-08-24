import click
from flask.cli import with_appcontext
from .routes import bp as dimensions_bp

def init_app(app):
    app.register_blueprint(dimensions_bp)

    @app.cli.command("seed-dimensions")
    @with_appcontext
    def seed_dimensions_cmd():
        """Carga dimensiones base (ACCOUNT, ENTITY, COSTCENTER, SCENARIO, TIME)."""
        from .seed import seed_dimensions
        seed_dimensions()
        click.echo("Seed OK")
