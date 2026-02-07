import os
from flask import Flask, render_template
from sqlalchemy import text

from db import db

# Blueprints
from routes.registrarse.registrarse import registro_bp
from routes.login.login import login_bp
from routes.dashboard.dashboard import dashboard_bp

app = Flask(__name__)

# ---------------- CONFIG GENERAL ----------------
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "clave_segura_123")
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

# ---------------- DATABASE (RAILWAY READY) ----------------
database_url = os.environ.get("DATABASE_URL")

if not database_url:
    # Fallback SOLO para local
    database_url = "postgresql+psycopg://postgres:postgres@localhost:5432/villar_peticiones"
else:
    # Ajuste necesario para SQLAlchemy 2 + psycopg3
    database_url = database_url.replace(
        "postgresql://",
        "postgresql+psycopg://"
    )

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ---------------- INIT DB ----------------
db.init_app(app)

# ---------------- BLUEPRINTS ----------------
app.register_blueprint(registro_bp)
app.register_blueprint(login_bp)
app.register_blueprint(dashboard_bp)

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template("index.html")

# ---------------- DB CHECK + CREATE TABLES ----------------
with app.app_context():
    try:
        # Prueba REAL de conexión a PostgreSQL
        result = db.session.execute(text("SELECT 1"))
        print("🔥 CONEXIÓN A POSTGRES OK:", result.scalar())

        # Crear tablas automáticamente
        db.create_all()
        print("✅ Tablas creadas correctamente")

    except Exception as e:
        print("❌ ERROR DE BASE DE DATOS:")
        print(e)

# ---------------- RUN LOCAL ----------------
# Railway usa Gunicorn automáticamente
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
