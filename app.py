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

# --- DATABASE URL CLEANUP ---
database_url = os.environ.get("DATABASE_URL", "").strip()
if database_url:
    # Eliminar cualquier parámetro previo
    if "?" in database_url:
        database_url = database_url.split("?")[0]
    
    # Forzar protocolo Psycopg 3
    database_url = database_url.replace("postgres://", "postgresql+psycopg://")
    database_url = database_url.replace("postgresql://", "postgresql+psycopg://")
    
    # Forzar desactivación de SSL para red interna
    database_url += "?sslmode=disable"
else:
    database_url = "postgresql+psycopg://postgres:postgres@localhost:5432/villar_peticiones"

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Blueprints
app.register_blueprint(registro_bp)
app.register_blueprint(login_bp)
app.register_blueprint(dashboard_bp)

@app.route('/')
def home():
    return render_template('index.html')

# --- HEALTHCHECK DINÁMICO ---
@app.route('/health')
def health():
    return "OK", 200

# CREACIÓN DE TABLAS (Solo si no existen)
# Lo envolvemos para que un error aquí no mate la app entera (evita el 502)
try:
    with app.app_context():
        db.create_all()
        print("Base de datos lista.")
except Exception as e:
    print(f"Error preventivo de DB: {e}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)