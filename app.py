from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Reword(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200))


@app.route('/')
def hello_world():
    data = Reword.query.all();
    return render_template('index.html',date=data)


@app.route('/add', methods=['POST'])
def add():
    reword_text = request.form['reword']
    new_reword = Reword(reword=reword_text)
    db.session.add(new_reword)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
