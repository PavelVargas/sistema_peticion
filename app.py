import os
import time
from flask import Flask, render_template
from db import db

# Importar Blueprints
from routes.registrarse.registrarse import registro_bp
from routes.login.login import login_bp
from routes.dashboard.dashboard import dashboard_bp

app = Flask(__name__)

# --- CONFIGURACIÓN DE ARCHIVOS ---
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- CONFIGURACIÓN DE BASE DE DATOS ---
database_url = os.environ.get("DATABASE_URL")

if database_url:
    database_url = database_url.strip()
    # 1. Asegurar el dialecto correcto para Psycopg 3
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif "postgresql+psycopg://" not in database_url:
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    
    # 2. Forzar sslmode=disable para evitar el error de startup packet en red interna
    if "?" in database_url:
        # Si ya tiene parámetros, quitamos sslmode previo y ponemos disable
        base_url = database_url.split("?")[0]
        database_url = f"{base_url}?sslmode=disable"
    else:
        database_url += "?sslmode=disable"
else:
    # Local
    database_url = "postgresql+psycopg://postgres:postgres@localhost:5432/villar_peticiones"

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.environ.get("SECRET_KEY", "clave_segura_123")

# --- INICIALIZACIÓN ---
db.init_app(app) 

# --- REGISTRO DE RUTAS ---
app.register_blueprint(registro_bp)
app.register_blueprint(login_bp)
app.register_blueprint(dashboard_bp)

@app.route('/')
def home():
    return render_template('index.html')

# --- CREACIÓN DE TABLAS (PROCESO DE ARRANQUE) ---
with app.app_context():
    for i in range(5):
        try:
            db.create_all()
            print("--- SISTEMA: Base de datos conectada y tablas listas ---")
            break
        except Exception as e:
            print(f"--- SISTEMA: Intento {i+1} de conexion fallido. Reintentando... {e}")
            time.sleep(5)

# --- INICIO DEL SERVIDOR ---
if __name__ == '__main__':
    # Railway inyecta el puerto automáticamente
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)