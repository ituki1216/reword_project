import json
from datetime import timedelta, datetime

from flask import Flask, jsonify, render_template, flash, url_for
from flask import request, redirect, session
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import random,os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = random.random()
app.secret_key = 'timer'
app.permanent_session_lifetime = timedelta(minutes=5)  # -> 5分 #(days=5) -> 5日保存

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)
migrate = Migrate(app, db)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True) #primaryは連番かつ一意な値 データベースの**主キー（primary key）**として設定されたフィールドが、各レコードごとに一意な（他のレコードと重複しない）値を持ち、さらにその値が連続して増加することを指します。以下に詳しく説明します。
    name = db.Column(db.String(30), nullable=False)
    mail_address = db.Column(db.String(140), nullable=False, unique=True) #uniqueデータベースのフィールドに対して一意制約を設けるためのオプションです。これにより、そのフィールドの値が他のレコードと重複しないように強制されます
    password = db.Column(db.String(120)) #hash化する可能性ある１２０


class UserPoints(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    points = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer)

class UserPointsHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    points = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.now())

class Reword(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    reword_kind = db.Column(db.Boolean)
    description = db.Column(db.String(200))
    user_id = db.Column(db.Integer)
    point = db.Column(db.Integer)


points = 0


@app.route('/')
@login_required
def Home():
    small_reword_arr = []
    big_reword_arr = []
    user_id = current_user.get_id()
    total_points = UserPoints.query.filter(UserPoints.user_id==user_id).first()
    small_reword = Reword.query.filter(Reword.reword_kind == 0)
    today_points = UserPointsHistory.query.filter(UserPointsHistory.user_id==user_id, UserPointsHistory.created_at >= datetime.now().date(), UserPointsHistory.created_at < datetime.now().date() +timedelta(days=1)).first()
    for data in small_reword:
        small_reword_arr.append(data.name)
    big_reword = Reword.query.filter(Reword.reword_kind == 1)
    for data in big_reword:
        big_reword_arr.append(data.name)
    return render_template('home/index.html', small_reword=json.dumps(small_reword_arr), big_reword=big_reword_arr, today_points=today_points, total_points=total_points)

def check_date(user_history):
    
    today = datetime.now().date()
    if today == user_history.created_at.date():
        return True
    else:
        return False
    

@app.route('/signup', methods=['GET'])
def sign():
    return render_template('register_rewords/signup.html')

@app.route('/signup', methods=['POST'])
def signup():
        username = request.form.get('name')        
        password = request.form.get('password')
        mail_address = request.form.get('mail_address')
        user = User(name=username, mail_address=mail_address, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        return redirect('login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(mail_address=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('ログイン成功しました！', 'success')
            return redirect(url_for('Home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
            print("test")
    return render_template('register_rewords/login.html') 

@app.route('/logout')
@login_required  # ログインしている場合のみアクセス可能
def logout():
    logout_user()  # ログアウト処理
    flash('You have been logged out!', 'info')  # フラッシュメッセージでログアウト完了を通知
    return redirect(url_for('Home'))  # ホームページにリダイレクト

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/add_points', methods=['POST'])
@login_required
def add_points():
    user_id = current_user.get_id()
    user = UserPoints.query.filter(UserPoints.user_id==user_id).first()  # 仮に1人のユーザーとして扱う場合
    user_history = UserPointsHistory.query.filter(
    UserPointsHistory.user_id == user_id,
    UserPointsHistory.created_at >= datetime.now().date(),
    UserPointsHistory.created_at < (datetime.now().date() + timedelta(days=1))
).first()
    if user_history is None:
        print('Aaa')
        user_history = UserPointsHistory(user_id=user_id, points=1)
    else:
        print(user_history.points)
        if check_date(user_history):
            user_history.points += 1
    user.points += 1  # 1ポイントを加算
    db.session.add(user)
    db.session.add(user_history)
    db.session.commit()
    return jsonify({'points': user.points})  # 最新のポイントを返す


@app.route('/get_points', methods=['GET'])
@login_required
def get_points():
    user_id = current_user.get_id()
    print(UserPointsHistory.query.first().points)
    user = UserPoints.query.filter(UserPoints.user_id==user_id).first() # 仮に1人のユーザーとして扱う場合 
    if user is None:
        user = UserPoints(points=0, user_id=user_id)
        db.session.add(user)
        db.session.commit()
    return jsonify({'points': user.points})


@app.route('/add', methods=['GET'])
@login_required
def add_get():
    small_reword = Reword.query.filter(Reword.reword_kind == 0, Reword.user_id == current_user.get_id())
    big_reword = Reword.query.filter(Reword.reword_kind == 1, Reword.user_id == current_user.get_id())
    return render_template('register_rewords/index.html', small_reword=small_reword, big_reword=big_reword)


@app.route('/update', methods=['POST'])
@login_required
def update():
    id = request.form["id"]
    name = request.form["reword"]
    reword = Reword.query.filter_by(id=id).first()
    reword.name = name
    db.session.commit()
    return redirect("/add")


@app.route('/delete', methods=['POST'])
@login_required
def delete():
    id = request.form["id"]
    record_to_delete = Reword.query.filter_by(id=id).first()
    db.session.delete(record_to_delete)
    db.session.commit()
    return redirect("/add")


@app.route('/create', methods=['POST'])
@login_required
def add():
    reword_kind = False
    if request.form.get('reword_kind') is not None:
        reword_kind = True
        points = random.randrange(300, 1000)
    else:
        reword_kind = False
        points = random.randrange(60, 299)
    reword_text = request.form['reword']
    user_id = current_user.get_id()
    new_reword = Reword(name=reword_text, reword_kind=reword_kind, user_id=user_id, point=points)
    db.session.add(new_reword)
    print(user_id, points)
    db.session.commit()
    return redirect("/add")


@app.route('/stopwatch')
@login_required
def stopwatch():
    user_id = current_user.get_id()
    return render_template('register_rewords/stopwatch.html', user_id=user_id)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
