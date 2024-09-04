from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import jsonify
import json

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

print("unti")
@app.route('/small_reword')
def small_reword_data():
    small_reword_arr = []
    small_reword = Reword.query.filter(Reword.reword_kind == 0)
    for data in small_reword:
        small_reword_arr.append(data.name)

    return jsonify(small_reword_arr)


@app.route('/big_reword')
def big_reword_data():
    big_reword_arr = []
    big_reword = Reword.query.filter(Reword.reword_kind == 1)
    for data in big_reword:
        big_reword_arr.append(data.name)

    return jsonify(big_reword_arr)


@app.route('/')
def Home():
    return render_template('home/index.html')


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


if __name__ == '__main__':
    app.run(debug=True)
