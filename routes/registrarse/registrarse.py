from flask import Flask,request,url_for,render_template,redirect
from db import db
from flask import Blueprint
from models.User.user import User

registro_bp = Blueprint('registro_bp',__name__)

@registro_bp.route('/registro' , methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        sucursal = request.form.get('sucursal')
        
        new_user = User(
            username=username,
            email=email,
            password=password,
            sucursal=sucursal,
            is_admin=False 
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login_bp.login'))
        except Exception as e:
            db.session.rollback()
            return f"Error al registrar: {str(e)}" 
    
    return render_template('registro/registro.html')
        
        