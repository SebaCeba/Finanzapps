from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    with open("scripts/crear_vista_hecho_financiero.sql", "r") as f:
        sql = f.read()
        db.session.execute(text(sql))  # 👈 aquí usamos `text()`
        db.session.commit()

    print("✅ Vista 'hecho_financiero' creada correctamente.")
