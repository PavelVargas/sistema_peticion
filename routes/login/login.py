from flask import Flask,request,url_for,render_template,redirect,session
from flask import Blueprint
from models.User.user import User

login_bp = Blueprint('login_bp',__name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect('/dashboard')
        else:
            redirect('login_bp.login')
            
    return render_template('login/login.html')

@login_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('dashboard_bp.dashboard'))