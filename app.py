from sqlalchemy import create_engine
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)


class Reword(db.Model):
    __tablename__ = 'rewords'
    id = db.Column(db.Integer, primary_key=True)
    reword = db.Column(db.String(200), nullable=False)


def create_tables():
    db.create_all()


@app.route('/')
def hello_world(): 
    data = Reword.query.all()
    return render_template('index.html', date=data)

@app.route('/add', methods=['POST'])
def add():
	reword_text = request.form['reword']
	new_reword = Reword(reword=reword_text)
	db.session.add(new_reword)
	db.session.commit()
	return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
