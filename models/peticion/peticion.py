from db import db
from datetime import datetime

class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    cantidad = db.Column(db.Integer, default=0)
    categoria = db.Column(db.String(50), default='General')

class Peticion(db.Model):
    __tablename__ = 'peticiones'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='Pendiente')
    archivo_adjunto = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    productos_solicitados = db.relationship('PeticionProducto', backref='peticion', lazy=True, cascade="all, delete-orphan")
    user = db.relationship('User', backref='peticiones_usuario')

class PeticionProducto(db.Model):
    __tablename__ = 'peticion_productos'
    id = db.Column(db.Integer, primary_key=True)
    peticion_id = db.Column(db.Integer, db.ForeignKey('peticiones.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad_solicitada = db.Column(db.Integer, nullable=False)

    producto = db.relationship('Producto')
    
class HistorialStock(db.Model):
    __tablename__ = 'historial_stock'
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'))
    cantidad = db.Column(db.Integer)
    tipo = db.Column(db.String(20)) 
    referencia = db.Column(db.String(100)) 
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    
    producto = db.relationship('Producto', backref='movimientos')