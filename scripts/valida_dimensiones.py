# scripts/valida_dimensiones.py
from pathlib import Path
import sqlite3, importlib.util, sys

OK = "✅"
ERR = "❌"
INF = "ℹ️"

def p(ok, msg): print(f"{OK if ok else ERR} {msg}")

root = Path(__file__).resolve().parents[1] if Path(__file__).parent.name == "scripts" else Path.cwd()

# --- 1) Template index.html
tmpl = root / "app" / "templates" / "dimensions" / "index.html"
if tmpl.exists():
    html = tmpl.read_text(encoding="utf-8", errors="ignore")
    must_have = [
        'Dimensiones (MVP mejorado)',
        'id="sel-dim"', 'id="frm-mem"', 'id="tbl-mem"',
        'id="sel-dim-h"', 'id="sel-hier"', 'id="frm-edge"',
        'Árbol (solo lectura)', 'id="btn-expand-all"', 'id="btn-collapse-all"'
    ]
    missing = [m for m in must_have if m not in html]
    p(not missing, f"Template OK: {tmpl.relative_to(root)}")
    if missing:
        print(f"{ERR} Falta en HTML → {', '.join(missing)}")
else:
    p(False, f"No existe template: {tmpl.relative_to(root)} (mueve el archivo aquí)")

# --- 2) App y rutas
try:
    sys.path.insert(0, str(root))
    from app import create_app
    app = create_app()
    with app.app_context():
        rules = sorted([(r.rule, ",".join(sorted(r.methods))) for r in app.url_map.iter_rules()])
        # buscamos endpoints clave
        needed = ["/api/dimensions", "/api/dimensions/<int:dim_id>/members",
                  "/api/dimensions/<int:dim_id>/hierarchies",
                  "/api/hierarchies/<int:hier_id>/tree",
                  "/api/hierarchies/<int:hier_id>/edges",
                  "/api/edges/<int:edge_id>", "/api/members/<int:member_id>"]
        present = {r for r,_ in rules}
        missing_rules = [r for r in needed if r not in present]
        p(not missing_rules, "Rutas API base presentes")
        if missing_rules:
            print(f"{ERR} Faltan rutas → {', '.join(missing_rules)}")

        # probamos un GET simple (puede devolver 200/302 según auth)
        c = app.test_client()
        r = c.get("/api/dimensions")
        if r.status_code in (200, 302):
            p(True, f"/api/dimensions responde {r.status_code}")
        else:
            p(False, f"/api/dimensions responde {r.status_code}")
except Exception as e:
    p(False, f"No pude crear la app: {e}")

# --- 3) DB / tablas y columnas
db_path = root / "instance" / "finanzas.db"
if db_path.exists():
    try:
        con = sqlite3.connect(db_path)
        q = lambda t: con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (t,)).fetchone() is not None
        dims_tables = ["dimensions","members","hierarchies","hierarchy_edges","member_aliases","member_properties"]
        miss = [t for t in dims_tables if not q(t)]
        p(not miss, "Tablas de dimensiones creadas")
        if miss:
            print(f"{ERR} Faltan tablas → {', '.join(miss)}")

        # columnas nuevas en hecho_financiero
        cols = [r[1] for r in con.execute("PRAGMA table_info(hecho_financiero)")]
        need_cols = ["account_id","entity_id","costcenter_id","scenario_id","time_id","moneda"]
        missc = [c for c in need_cols if c not in cols]
        p(not missc, "Columnas nuevas en hecho_financiero presentes")
        if missc:
            print(f"{ERR} Faltan columnas → {', '.join(missc)}")

    except Exception as e:
        p(False, f"Error revisando SQLite: {e}")
    finally:
        try: con.close()
        except: pass
else:
    p(False, f"No existe DB: {db_path.relative_to(root)} (¿corriste las migraciones?)")

# --- 4) Seed command / función
seed_paths = [
    root / "app" / "dimensions" / "seed.py",
    root / "app" / "dimensions" / "__init__.py",
]
found_seed = False
for sp in seed_paths:
    if sp.exists() and "seed" in sp.name:
        txt = sp.read_text(encoding="utf-8", errors="ignore")
        if "def seed_dimensions" in txt or "@app.cli.command(" in txt:
            found_seed = True
p(found_seed, "Seed de dimensiones detectado (función o comando)")

print(f"{INF} Terminado.")
