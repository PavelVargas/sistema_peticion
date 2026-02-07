from db import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(155), nullable=False)
    email = db.Column(db.String(155), unique=True, nullable=False)
    role = db.Column(db.String(50), default='usuario')
    sucursal = db.Column(db.String(100), unique=False, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    def __repr__(self):
        return f'Usuario {self.username}'
