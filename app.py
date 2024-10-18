import json # jon形式を扱うためのモジュール
from datetime import timedelta, datetime # 日付の取得

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField # form処理を簡単にする
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask import Flask, jsonify, render_template, flash, url_for
from flask import request, redirect, session
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import random,os
import logging


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = random.random()
login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = 'timer'
app.permanent_session_lifetime = timedelta(minutes=60)  # -> 5分 #(days=60) -> 5日保存


login_manager.login_message = "おかえりさない！ログインを行ってください!"


db = SQLAlchemy(app)
login_manager.login_view = 'login'
migrate = Migrate(app, db)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True) #primaryは連番かつ一意な値 データベースの**主キー（primary key）**として設定されたフィールドが、各レコードごとに一意な（他のレコードと重複しない）値を持ち、さらにその値が連続して増加することを指します。以下に詳しく説明します。
    name = db.Column(db.String(30), nullable=False)
    mail_address = db.Column(db.String(140), nullable=False, unique=True) #uniqueデータベースのフィールドに対して一意制約を設けるためのオプションです。これにより、そのフィールドの値が他のレコードと重複しないように強制されます
    password = db.Column(db.String(120)) #hash化する可能性ある１２０

class SignupForm(FlaskForm): #CRSF対策
    name = StringField('Name', validators=[DataRequired(), Length(max=20)])
    mail_address = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=140)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

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


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

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
        return render_template(
        'home/index.html', 
        small_reword=json.dumps(small_reword_arr), 
        big_reword=big_reword_arr, 
        today_points=today_points, 
        total_points=total_points)

def check_date(user_history):
    
    today = datetime.now().date()
    if today == user_history.created_at.date():
        return True
    else:
        return False


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('name')        
        password = request.form.get('password')
        mail_address = request.form.get('mail_address')

        existing_user = User.query.filter_by(mail_address=mail_address).first()
        if existing_user:
            flash('このメールアドレスは既に登録されています。', 'error')
            return render_template('register_rewords/signup.html', name=username, mail_address=mail_address)

        hashed_password = generate_password_hash(password)
        user = User(name=username, mail_address=mail_address, password=hashed_password)
        db.session.add(user)
        try:
            db.session.commit()
            flash('登録が完了しました。ログインしてください。', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('登録中にエラーが発生しました。もう一度お試しください。', 'error')
            return render_template('register_rewords/signup.html')

    return render_template('register_rewords/signup.html')


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
            flash('ログインに失敗しました。再度ログインを実行してください', 'danger')
            print("test")
    return render_template('register_rewords/login.html') 

@app.route('/logout')
@login_required  # ログインしている場合のみアクセス可能
def logout():
    logout_user()  # ログアウト処理
    flash('You have been logged out!', 'info')  # フラッシュメッセージでログアウト完了を通知
    return redirect(url_for('Home'))  # ホームページにリダイレクト

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

@app.route('/clear_cache')
def clear_cache():
    session.clear()  # セッションをクリア
    return redirect(url_for('Home'))  # トップページにリダイレクト

@app.route('/small_reword', methods=['GET']) #topページより送信されたsmall_rewordの情報を取得する
@login_required
def get_small_reword():
    user_id = current_user.get_id()
    rewords = []
    user_points = UserPoints.query.filter_by(user_id=user_id).first()
    small_reword = Reword.query.filter(Reword.reword_kind == 0, Reword.user_id == current_user.get_id()).all()
    print(user_points.points)
    for reword in small_reword:
        if int(user_points.points) >= int(reword.point):
            rewords.append(reword.name)
    if len(rewords):
        select_reword = rewords[random.randrange(0, len(rewords)-1)]
        small_reword = Reword.query.filter(Reword.reword_kind == 0, Reword.user_id == current_user.get_id(), Reword.name == select_reword).first()
        calc_points = user_points.points - small_reword.point
        user_points.points = calc_points
        db.session.commit()
        return jsonify({'reword': select_reword})
    return[]

@app.route('/big_reword', methods=['GET']) #topページより送信されたsmall_rewordの情報を取得する
@login_required
def get_big_reword():
    user_id = current_user.get_id()
    rewords = []
    user_points = UserPoints.query.filter_by(user_id=user_id).first()
    big_reword = Reword.query.filter(Reword.reword_kind == 1, Reword.user_id == current_user.get_id()).all()
    print(user_points.points)
    for reword in big_reword:
        if int(user_points.points) >= int(reword.point):
            rewords.append(reword.name)
    if len(rewords):
        select_reword = rewords[random.randrange(0, len(rewords)-1)]
        big_reword = Reword.query.filter(Reword.reword_kind == 1, Reword.user_id == current_user.get_id(), Reword.name == select_reword).first()
        calc_points = user_points.points - big_reword.point
        user_points.points = calc_points
        db.session.commit()
        return jsonify({'reword': select_reword})
    return[]



@app.route('/add', methods=['GET']) #addのページより送信された情報を取得して以下の関数を実行する
@login_required
def add_get():
    small_reword = Reword.query.filter(Reword.reword_kind == 0, Reword.user_id == current_user.get_id())
    big_reword = Reword.query.filter(Reword.reword_kind == 1, Reword.user_id == current_user.get_id())
    return render_template('register_rewords/index.html', small_reword=small_reword, big_reword=big_reword)


@app.route('/update', methods=['POST']) #Idのアップデートのリクエストをデータベースに送信する
@login_required
def update():
    id = request.form["id"]
    name = request.form["reword"]
    reword = Reword.query.filter_by(id=id).first()
    reword.name = name
    db.session.commit()
    return redirect("/add")


@app.route('/delete', methods=['POST']) #deleteしたIDの情報をデータベースの送信する
@login_required
def delete():
    id = request.form["id"]
    record_to_delete = Reword.query.filter_by(id=id).first() 
    db.session.delete(record_to_delete)
    db.session.commit()
    return redirect("/add")


@app.route('/create', methods=['POST']) #作成したrewordの情報をデータベースに送信する
@login_required
def add():
    reword_kind = False
    if request.form.get('reword_kind') is not None:
        reword_kind = True
        points = random.randrange(1, 2)
    else:
        reword_kind = False
        points =  random.randrange(3, 4)
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

@app.route('/GoHome', methods=['POST'])
def GoHome():
    return redirect(url_for('Home'))  # ホームページにリダイレクト





if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    #app.run(debug=True)
