import os
from flask import Flask, render_template
from db import db

# Blueprints
from routes.registrarse.registrarse import registro_bp
from routes.login.login import login_bp
from routes.dashboard.dashboard import dashboard_bp

app = Flask(__name__)

# ---------------- CONFIG ----------------
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "clave_segura_123")
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

# -------- DATABASE (Railway READY) -------
database_url = os.environ.get("DATABASE_URL")

if database_url:
    database_url = database_url.replace(
        "postgres://",
        "postgresql+psycopg://"
    )
else:
    database_url = "postgresql+psycopg://postgres:postgres@localhost:5432/villar_peticiones"

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Init DB
db.init_app(app)

# Blueprints
app.register_blueprint(registro_bp)
app.register_blueprint(login_bp)
app.register_blueprint(dashboard_bp)

@app.route("/")
def home():
    return render_template("index.html")

# -------- CREATE TABLES (SAFE) -----------
with app.app_context():
    try:
        db.create_all()
        print("✅ Base de datos conectada y tablas creadas")
    except Exception as e:
        print(f"❌ Error DB: {e}")

# ⚠️ Railway usa Gunicorn, esto es solo local
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
