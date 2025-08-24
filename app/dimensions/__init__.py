from .routes import bp as dimensions_bp

def init_app(app):
    app.register_blueprint(dimensions_bp)