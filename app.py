import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# =========================
# CONFIGURACIÓN BASE
# =========================

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("❌ DATABASE_URL no está definido en Railway")

# Fix para postgres:// → postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "super-secret-key"

db = SQLAlchemy(app)

print("✅ DATABASE_URL cargado correctamente")

# =========================
# MODELO USER
# =========================

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default="user")
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<User {self.email}>"

# =========================
# CREAR TABLAS Y ADMIN
# =========================

with app.app_context():
    try:
        db.create_all()
        print("✅ Tablas creadas/verificadas")

        admin = User.query.filter_by(email="admin@villar.com").first()

        if not admin:
            admin = User(
                name="admin_villar",
                email="admin@villar.com",
                password="admin",  # ❗ sin encriptar (como pediste)
                role="admin",
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuario admin creado correctamente")
        else:
            print("ℹ️ Usuario admin ya existe")

    except Exception as e:
        print("❌ ERROR DE BASE DE DATOS")
        print(e)
        raise e

# =========================
# RUTA DE PRUEBA
# =========================

@app.route("/")
def home():
    return "🚀 Flask + PostgreSQL + Railway funcionando correctamente"

# =========================
# ENTRYPOINT LOCAL
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
