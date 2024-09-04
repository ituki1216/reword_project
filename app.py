from flask import Flask, render_template, request, redirect, url_for # flask(ルート機能を定義), render_template(htmlファイルを表示するため), request(ユーザーがデータベースに情報を送る), ridirect(とあるページから別のページに移動したいときに使用), url_for(関数名を使用して動的にURLを生成する)
from flask_sqlalchemy import SQLAlchemy # sqlalchemy(データベース操作を簡単に行う)
from flask_migrate import Migrate # Migrate(データテーブルを変更、追加、削除したときにそのデータを反映させるためのもの)
from datetime import datetime # datetime(現在の日付を取得)
from datetime import deltatime # deltatime(経過日時を取得)
import random # random(乱数を生成するためのモジュール)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Reword(db.Model): # データベースの作成 
    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(80), nullable=False)
    reword_kind = db.Column(db.Boolean)
    description = db.Column(db.String(200))
   


@app.route('/') # toppageにアクセスされたときにHome関数を実行するよ！！！あは！ (現在時刻2024/09/04/15:23:35) はーむずすぎてちぬ
def Home(): # ユーザーに見せるホームページにまつわる関数
    double_point_day = set_or_get_double_point_day() # ポイント２倍dayを設定
    small_reword_arr = [] # 空のリストであり報酬を格納するためのリスト
    big_reword_arr = [] # 上同様、空のリストであり報酬を格納する
    small_reword = Reword.query.filter(Reword.reword_kind == 0) # small_rewordはrewordデータベースから0を取り出しsmallとする
    for data in small_reword:
        small_reword_arr.append({'name':data.name, 'timestamp': data.timestamp}) # 小さなご褒美をデータベースから取得する
    big_reword = Reword.query.filter(Reword.reword_kind == 1)
    for data in big_reword:
        big_reword_arr.append(data.name) # 上に同じ大きなご褒美を取得する
    return render_template('home/index.html', small_reword=small_reword_arr, big_reword=big_reword_arr) # strftime('%A, %B %d, %Y')) 今日が2倍point dayならtopページに表示を行う

@app.route('/', methods=['POST']) # ユーザーからpostされたデータをrewordに追加
def add():
    reword_kind = False # reword_kindの変数を初期化
    print(request.form) # 弟馬具用
    if  request.form.get('reword_kind'): # もしれクエストがreword_kindならTRUE 大きなご褒美とする
        reword_kind = True
    reword_text = request.form['reword'] # rewordの名前はformのrewordを参照
    new_reword = Reword(name = reword_text, reword_kind = reword_kind) # Userから受け取ったrewordの名前、種類はそれぞれreword_text, rewird_kindとする)
    db.session.add(new_reword) # 追加されたrewordをデータベースに追加し
    db.session.commit() # commitする
    return redirect("/add") # Userにはadd画面に戻ってもらう
    
@app.route('/add', methods=['GET'])
def hello_world(): # /addにUserがアクセスしたときに以下の関数が実行される
    small_reword = Reword.query.filter(Reword.reword_kind == 0) # rewordというテーブルから条件にあうrewordを取得(reword == 0)
    big_reword = Reword.query.filter(Reword.reword_kind == 1) # rewordのクエリーの条件検索(reword == 1)を取得
    return render_template('register_rewords/index.html',small_reword=small_reword, big_reword=big_reword) # topページに返すとともに small_reword=small_reword, big_reword=big_rewordデータをわたす
    
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

if __name__ == '__main__':
    app.run(debug=True)
