import json
from datetime import timedelta

from flask import Flask, jsonify, render_template
from flask import request, redirect, session
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'timer'
app.permanent_session_lifetime = timedelta(minutes=5)  # -> 5分 #(days=5) -> 5日保存

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class UserPoints(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    points = db.Column(db.Integer, default=0)


class Reword(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    reword_kind = db.Column(db.Boolean)
    description = db.Column(db.String(200))


points = 0


@app.route('/')
def Home():
    small_reword_arr = []
    big_reword_arr = []
    small_reword = Reword.query.filter(Reword.reword_kind == 0)
    for data in small_reword:
        small_reword_arr.append(data.name)
    big_reword = Reword.query.filter(Reword.reword_kind == 1)
    for data in big_reword:
        big_reword_arr.append(data.name)
    return render_template('home/index.html', small_reword=json.dumps(small_reword_arr), big_reword=big_reword_arr,
                           points=UserPoints)


@app.route("/", methods=["GET"])
def test():
    session.permanent = True
    timer = request.form["timer"]
    session["timer"] = timer


@app.route('/add_points', methods=['POST'])
def add_points():
    user = UserPoints.query.first()  # 仮に1人のユーザーとして扱う場合
    if user is None:
        user = UserPoints(points=0)
        db.session.add(user)
    user.points += 1  # 1ポイントを加算
    db.session.commit()
    return jsonify({'points': user.points})  # 最新のポイントを返す


@app.route('/get_points', methods=['GET'])
def get_points():
    user = UserPoints.query.first()  # 仮に1人のユーザーとして扱う場合
    if user is None:
        user = UserPoints(points=0)
        db.session.add(user)
        db.session.commit()
    return jsonify({'points': user.points})


@app.route('/add', methods=['GET'])
def hello_world():
    small_reword = Reword.query.filter(Reword.reword_kind == 0)
    big_reword = Reword.query.filter(Reword.reword_kind == 1)
    return render_template('register_rewords/index.html', small_reword=small_reword, big_reword=big_reword)


@app.route('/update', methods=['POST'])
def update():
    id = request.form["id"]
    name = request.form["reword"]
    reword = Reword.query.filter_by(id=id).first()
    reword.name = name
    db.session.commit()
    return redirect("/add")


@app.route('/delete', methods=['POST'])
def delete():
    id = request.form["id"]
    record_to_delete = Reword.query.filter_by(id=id).first()
    db.session.delete(record_to_delete)
    db.session.commit()
    return redirect("/add")


@app.route('/create', methods=['POST'])
def add():
    reword_kind = False
    print(request.form)
    if request.form.get('reword_kind'):
        reword_kind = True
    reword_text = request.form['reword']
    new_reword = Reword(name=reword_text, reword_kind=reword_kind)
    db.session.add(new_reword)
    db.session.commit()
    return redirect("/add")


@app.route('/stopwatch')
def stopwatch():
    return render_template('register_rewords/stopwatch.html')


if __name__ == '__main__':
    app.run(debug=True)
