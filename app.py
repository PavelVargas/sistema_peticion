import os
from flask import Flask, render_template
from db import db

# Importar Blueprints
from routes.registrarse.registrarse import registro_bp
from routes.login.login import login_bp
from routes.dashboard.dashboard import dashboard_bp

app = Flask(__name__)

# --- CONFIGURACIÓN ---
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = os.environ.get("SECRET_KEY", "clave_segura_123")

# --- PROCESAMIENTO DE DATABASE_URL ---
database_url = os.environ.get("DATABASE_URL", "").strip()

if database_url:
    # 1. Limpiar parámetros si existen (para evitar conflictos de SSL)
    if "?" in database_url:
        database_url = database_url.split("?")[0]
    
    # 2. Corregir protocolo para SQLAlchemy 2.0 + Psycopg 3
    database_url = database_url.replace("postgres://", "postgresql+psycopg://")
    database_url = database_url.replace("postgresql://", "postgresql+psycopg://")
    
    # 3. Desactivar SSL para la conexión interna de Railway (.internal)
    database_url += "?sslmode=disable"
else:
    # Local
    database_url = "postgresql+psycopg://postgres:postgres@localhost:5432/villar_peticiones"

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicializar DB
db.init_app(app)

# Registro de Blueprints
app.register_blueprint(registro_bp)
app.register_blueprint(login_bp)
app.register_blueprint(dashboard_bp)

@app.route('/')
def home():
    return render_template('index.html')

# --- INICIALIZACIÓN DE TABLAS (Sin bloquear el arranque) ---
with app.app_context():
    try:
        db.create_all()
        print("--- SISTEMA: Base de datos configurada correctamente ---")
    except Exception as e:
        print(f"--- ERROR DE DB: {e} ---")

if __name__ == '__main__':
    # Puerto dinámico de Railway o 5000 en local
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)