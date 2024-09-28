import json
from datetime import timedelta, datetime

from flask import Flask, jsonify, render_template, flash, url_for
from flask import request, redirect, session
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_caching import Cache
import random
import os
import logging

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24))
app.permanent_session_lifetime = timedelta(minutes=60)  

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "おかえりなさい！ログインを行ってください。"

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

csrf = CSRFProtect(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(30), nullable=False)
    mail_address = db.Column(db.String(140), nullable=False, unique=True, index=True)
    password = db.Column(db.String(120), nullable=False)
    points = db.relationship('UserPoints', backref='user', uselist=False, cascade="all, delete-orphan")
    rewards = db.relationship('Reward', backref='user', lazy=True, cascade="all, delete-orphan")
    points_history = db.relationship('UserPointsHistory', backref='user', lazy=True, cascade="all, delete-orphan")

class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    reward_kind = db.Column(db.Boolean, nullable=False) 
    description = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    point = db.Column(db.Integer, nullable=False)

class UserPoints(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    points = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class UserPointsHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    points = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Login')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/')
@login_required
def home():
    small_reward_arr = []
    big_reward_arr = []
    user_id = current_user.get_id()
    
    user_points = UserPoints.query.filter_by(user_id=user_id).first()
    if not user_points:
        user_points = UserPoints(user_id=user_id, points=0)
        db.session.add(user_points)
        db.session.commit()
    
    total_points = user_points.points
    
    small_rewards = Reward.query.filter_by(reward_kind=False, user_id=user_id).all()
    big_rewards = Reward.query.filter_by(reward_kind=True, user_id=user_id).all()
    
    small_reward_arr = [reward.name for reward in small_rewards]
    big_reward_arr = [reward.name for reward in big_rewards]
    
    today = datetime.utcnow().date()
    tomorrow = today + timedelta(days=1)
    today_points = UserPointsHistory.query.filter(
        UserPointsHistory.user_id == user_id,
        UserPointsHistory.created_at >= today,
        UserPointsHistory.created_at < tomorrow
    ).first()
    
    return render_template(
        'home/index.html', 
        small_rewards=json.dumps(small_reward_arr), 
        big_rewards=big_reward_arr, 
        today_points=today_points, 
        total_points=total_points
    )

def check_date(user_history):
    today = datetime.utcnow().date()
    return today == user_history.created_at.date()

@app.route('/signup', methods=['POST'])
def signup():
    try:
        username = request.form.get('name')
        password = request.form.get('password')
        mail_address = request.form.get('mail_address')
        
        if User.query.filter_by(mail_address=mail_address).first():
            flash('このメールアドレスは既に使用されています。', 'danger')
            return redirect(url_for('sign'))
        
        hashed_password = generate_password_hash(password)
        user = User(name=username, mail_address=mail_address, password=hashed_password)
        
        db.session.add(user)
        db.session.commit()
        
        user_points = UserPoints(user_id=user.id, points=0)
        user_history = UserPointsHistory(user_id=user.id, points=0)
        db.session.add(user_points)
        db.session.add(user_history)
        db.session.commit()
        
        flash('登録が完了しました。ログインしてください。', 'success')
        return redirect(url_for('login'))
    except Exception as e:
        logger.error(f"サインアップ中にエラーが発生しました: {e}")
        flash('登録に失敗しました。再度お試しください。', 'danger')
        return redirect(url_for('sign'))

@app.route('/signup', methods=['GET'])
def sign():
    return render_template('register_rewards/signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(mail_address=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('ログイン成功しました！', 'success')
            return redirect(url_for('home'))
        else:
            flash('ログインに失敗しました。再度ログインを実行してください', 'danger')
    return render_template('register_rewards/login.html', form=form)  

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out!', 'info')
    return redirect(url_for('login'))  

@app.route('/add_points', methods=['POST'])
@login_required
def add_points():
    user_id = current_user.get_id()
    user_points = UserPoints.query.filter_by(user_id=user_id).first()
    
    if not user_points:
        user_points = UserPoints(user_id=user_id, points=0)
        db.session.add(user_points)
        db.session.commit()
    
    today = datetime.utcnow().date()
    tomorrow = today + timedelta(days=1)
    
    user_history = UserPointsHistory.query.filter(
        UserPointsHistory.user_id == user_id,
        UserPointsHistory.created_at >= today,
        UserPointsHistory.created_at < tomorrow
    ).first()
    
    if user_history is None:
        user_history = UserPointsHistory(user_id=user_id, points=1)
    else:
        if check_date(user_history):
            user_history.points += 1
    
    user_points.points += 1 
    
    db.session.add(user_points)
    db.session.add(user_history)
    db.session.commit()
    
    return jsonify({'points': user_points.points})

@app.route('/get_points', methods=['GET'])
@login_required
def get_points():
    user_id = current_user.get_id()
    user_points = UserPoints.query.filter_by(user_id=user_id).first()
    
    if not user_points:
        user_points = UserPoints(user_id=user_id, points=0)
        db.session.add(user_points)
        db.session.commit()
    
    return jsonify({'points': user_points.points})

@app.route('/clear_cache')
def clear_cache_route():
    session.clear()
    return redirect(url_for('home'))

@app.route('/small_reward', methods=['GET']) 
def get_small_reward():
    user_id = current_user.get_id()
    user_points = UserPoints.query.filter_by(user_id=user_id).first()
    
    if not user_points:
        flash('ポイントが存在しません。', 'danger')
        return redirect(url_for('home'))
    
    small_rewards = Reward.query.filter_by(reward_kind=False, user_id=user_id).all()
    eligible_rewards = [reward.name for reward in small_rewards if user_points.points >= reward.point]
    
    if eligible_rewards:
        selected_reward_name = random.choice(eligible_rewards)
        selected_reward = Reward.query.filter_by(name=selected_reward_name, user_id=user_id, reward_kind=False).first()
        user_points.points -= selected_reward.point
        db.session.commit()
        return jsonify({'reward': selected_reward.name})
    
    return jsonify({'reward': None})

@app.route('/add', methods=['GET'])
@login_required
def add_get():
    user_id = current_user.get_id()
    small_rewards = Reward.query.filter_by(reward_kind=False, user_id=user_id).all()
    big_rewards = Reward.query.filter_by(reward_kind=True, user_id=user_id).all()
    return render_template('register_rewards/index.html', small_rewards=small_rewards, big_rewards=big_rewards)

@app.route('/update', methods=['POST'])
@login_required
def update_reward():
    try:
        reward_id = request.form.get("id")
        new_name = request.form.get("reward")
        
        reward = Reward.query.filter_by(id=reward_id, user_id=current_user.get_id()).first()
        if not reward:
            flash('報酬が見つかりません。', 'danger')
            return redirect(url_for('add_get'))
        
        reward.name = new_name
        db.session.commit()
        flash('報酬が更新されました。', 'success')
        return redirect(url_for('add_get'))
    except Exception as e:
        logger.error(f"報酬の更新中にエラーが発生しました: {e}")
        flash('報酬の更新に失敗しました。再度お試しください。', 'danger')
        return redirect(url_for('add_get'))

@app.route('/delete', methods=['POST'])
@login_required
def delete_reward():
    try:
        reward_id = request.form.get("id")
        reward = Reward.query.filter_by(id=reward_id, user_id=current_user.get_id()).first()
        if not reward:
            flash('報酬が見つかりません。', 'danger')
            return redirect(url_for('add_get'))
        
        db.session.delete(reward)
        db.session.commit()
        flash('報酬が削除されました。', 'success')
        return redirect(url_for('add_get'))
    except Exception as e:
        logger.error(f"報酬の削除中にエラーが発生しました: {e}")
        flash('報酬の削除に失敗しました。再度お試しください。', 'danger')
        return redirect(url_for('add_get'))

@app.route('/create', methods=['POST'])
@login_required
def create_reward():
    try:
        reward_kind = request.form.get('reward_kind') == 'on'
        if reward_kind:
            points = random.randint(300, 1000)
        else:
            points = 0 
        
        reward_text = request.form.get('reward')
        user_id = current_user.get_id()
        
        new_reward = Reward(
            name=reward_text,
            reward_kind=reward_kind,
            description=request.form.get('description', ''),
            user_id=user_id,
            point=points
        )
        
        db.session.add(new_reward)
        db.session.commit()
        
        flash('報酬が追加されました。', 'success')
        return redirect(url_for('add_get'))
    except Exception as e:
        logger.error(f"報酬の作成中にエラーが発生しました: {e}")
        flash('報酬の作成に失敗しました。再度お試しください。', 'danger')
        return redirect(url_for('add_get'))

@app.route('/stopwatch')
@login_required
def stopwatch():
    user_id = current_user.get_id()
    return render_template('register_rewards/stopwatch.html', user_id=user_id)

@app.route('/test_points', methods=['POST'])
def test_add_points():
    try:
        user_id = current_user.get_id()
        user_points = UserPoints.query.filter_by(user_id=user_id).first()
        if not user_points:
            user_points = UserPoints(user_id=user_id, points=0)
            db.session.add(user_points)
        
        user_points.points += 1000
        db.session.commit()
        
        logger.info(f"ポイントが付与されました。現在のポイント: {user_points.points}")
        flash("1000ポイントを付与しました", "success")
    except Exception as e:
        logger.error(f"ポイント付与中にエラーが発生しました: {e}")
        flash('ポイントの付与に失敗しました。再度お試しください。', 'danger')
    finally:
        return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)