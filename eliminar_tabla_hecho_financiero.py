from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    db.session.execute(text("DROP TABLE hecho_financiero"))
    db.session.commit()
    print("✅ Tabla 'hecho_financiero' eliminada correctamente.")
