from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, 
from datetime import datetime
from datetime import deltatime
import random



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Reword(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    reword_kind = db.Column(db.Boolean)
    description = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow) # エラーなぜ？
    start_of_week = db.Column(db.DateTime, nullable=False)
    double_points_day = db.Column(db.DateTime, nullable=False)

# 一週間の始まりを月日とする
def get_start_week(date)
    start = date - timedelta(days=date. weekday())

#　ランダムでポイント2倍dayを決定
def double_point_day(start_week)
    random_double_day = random.randint(0, 6) # 一週間のうランダムに２倍の火を６日間の中から決定
    return start_week + timedelta(days=random_double_day)

@app.route('/add', methods=['GET'])
def hello_world():
    small_reword = Reword.query.filter(Reword.reword_kind == 0)
    big_reword = Reword.query.filter(Reword.reword_kind == 1)
    return render_template('register_rewords/index.html',small_reword=small_reword, big_reword=big_reword)

@app.route('/')
def Home(): #zz
    small_reword_arr = []
    big_reword_arr = []
    small_reword = Reword.query.filter(Reword.reword_kind == 0)
    for data in small_reword:
        small_reword_arr.append(data.name)
    big_reword = Reword.query.filter(Reword.reword_kind == 1)
    for data in big_reword:
        big_reword_arr.append('name': data.name, 'timestamp': data.timestamp)
    return render_template('home/index.html', small_reword=small_reword_arr, big_reword=big_reword_arr)

@app.route('/delete', methods=['POST'])
def delete():
    id = request.form["id"]
    record_to_delete = Reword.query.filter_by(id=id).first()
    db.session.delete(record_to_delete)
    db.session.commit()
    return redirect("/add")

@app.route('/update', methods=['POST'])
def update():
    id = request.form["id"]
    name = request.form["reword"]
    reword = Reword.query.filter_by(id=id).first()
    reword.name = name
    db.session.commit()
    return redirect("/add")

@app.route('/', methods=['POST'])
def add():
    reword_kind = False
    print(request.form)
    if  request.form.get('reword_kind'):
        reword_kind = True
    reword_text = request.form['reword']
    new_reword = Reword(name = reword_text, reword_kind = reword_kind)
    db.session.add(new_reword)
    db.session.commit()
    return redirect("/add")


if __name__ == '__main__':
    app.run(debug=True)
