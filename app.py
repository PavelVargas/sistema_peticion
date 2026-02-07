import os
from flask import Flask, render_template
from sqlalchemy import text
from db import db
from models.User.user import User

# Blueprints
from routes.registrarse.registrarse import registro_bp
from routes.login.login import login_bp
from routes.dashboard.dashboard import dashboard_bp

# --------------------------------------------------
# APP
# --------------------------------------------------
app = Flask(__name__)

# --------------------------------------------------
# CONFIG GENERAL
# --------------------------------------------------
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "clave_segura_123")
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

# --------------------------------------------------
# DATABASE (RAILWAY / LOCAL)
# --------------------------------------------------
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace(
            "postgres://", "postgresql+psycopg://", 1
        )
    elif DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace(
            "postgresql://", "postgresql+psycopg://", 1
        )
else:
    # SOLO desarrollo local
    DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/villar_peticiones"

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# --------------------------------------------------
# INIT DB
# --------------------------------------------------
db.init_app(app)

# --------------------------------------------------
# BLUEPRINTS
# --------------------------------------------------
app.register_blueprint(registro_bp)
app.register_blueprint(login_bp)
app.register_blueprint(dashboard_bp)

# --------------------------------------------------
# ROUTES
# --------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")

# --------------------------------------------------
# DB INIT + ADMIN CREATION
# --------------------------------------------------
with app.app_context():
    try:
        # Probar conexión real
        result = db.session.execute(text("SELECT 1"))
        print("🔥 CONEXIÓN A POSTGRES OK:", result.scalar())

        # Crear tablas
        db.create_all()
        print("✅ Tablas creadas")

        # Crear admin por defecto
        admin = User.query.filter_by(email="admin@villar.com").first()

        if not admin:
            admin = User(
                name="admin_villar",
                email="admin@villar.com",
                password="admin",
                role="admin",
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("👑 Usuario admin creado correctamente")
        else:
            print("ℹ️ Usuario admin ya existe")

    except Exception as e:
        print("❌ ERROR DE BASE DE DATOS")
        print(e)

# --------------------------------------------------
# RUN
# --------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
