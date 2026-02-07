import os # Importante para carpetas
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from db import db
from werkzeug.utils import secure_filename # Para nombres de archivos seguros

from routes.registrarse.registrarse import registro_bp
from routes.login.login import login_bp
from routes.dashboard.dashboard import dashboard_bp

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg://postgres:postgres@localhost:5432/villar_peticiones"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'clave'

db.init_app(app) 

app.register_blueprint(registro_bp)
app.register_blueprint(login_bp)
app.register_blueprint(dashboard_bp)

@app.route('/')
def home():
    return render_template('index.html')

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')