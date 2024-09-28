from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User, UserPoints

auth_bp = Blueprint('auth', __name__, template_folder='../templates/register_rewords')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('name')        
        password = request.form.get('password')
        mail_address = request.form.get('mail_address')
        
        # ユーザーの存在チェック
        existing_user = User.query.filter_by(mail_address=mail_address).first()
        if existing_user:
            flash('このメールアドレスは既に使用されています。', 'danger')
            return redirect(url_for('auth.signup'))
        
        # 新規ユーザー作成
        user = User(
            name=username, 
            mail_address=mail_address, 
            password=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        # ユーザーポイントの初期化
        user_points = UserPoints(user_id=user.id)
        db.session.add(user_points)
        db.session.commit()
        
        flash('登録が完了しました。ログインしてください。', 'success')
        return redirect(url_for('auth.login'))
    return render_template('signup.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(mail_address=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('ログイン成功しました！', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('ログインに失敗しました。再度ログインを実行してください', 'danger')
    return render_template('login.html') 

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out!', 'info')
    return redirect(url_for('main.home'))
