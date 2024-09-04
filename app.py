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
<<<<<<< HEAD
    timestamp = db.Column(db.DateTime, default=datetime.utcnow) # エラーなぜ？
    start_week = db.Column(db.DateTime, nullable=False) 
    double_point_day = db.Column(db.DateTime, nullable=False)


# 特定の週の開始日にポイントを２倍にして、データベースに取得、保存
# 週に開始日時を取得
today = datetime.uncnow() # 現在の日時を取得
start_week = get_start_week(today)) # 今日が属している州の始まりを取得
# ランダムで2倍の日を取得
double_point_day = datermine_double_point_day(start_week) 

# 一週間の始まりを㈪とする
def get_start_week(date) # dateを引数とて受け取り週の始まりを計算
    start = date - timedelta(days=date. weekday()) # 現在の日付からその日が週の何日目かを計算(-)して始まりを計算
    return start # 計算した週の開始日を返す

#　ランダムでポイント2倍dayを決定
def double_point_day(start_week)
    random_double_day = random.randint(0, 6) # 一週間のうランダムに2倍の火を7日間の中から決定
    return start_week + timedelta(days=random_double_day) #週の初めにランダムな日を返す 

def set_double_point_day(): # 今日の日付をもとに、その週の２倍の火を取得 else設定
    today = datetime.uncnow() # 現在の日付を取得
    start_week = get_start_week(today) # 現在の日付をもとに今日が属する週の初めを取得 
    weekly_config = Weekly.Config.query.filter_by(start_week=start_week).first() # その週の規定が存在するか否かfilter(検索)
    if weekly_config: # もしあれば
          return weekly_config.double_point_day # その週を２倍に
    else: # もしなければ
        double_point_day = datermine_double_point_day(start_week) #週の開始日をもとにランダムな２倍dayを設定し直す
        new_weekly_config = WeeklyConfing(start_week=start_week, double_point_day=double_point_day) #現在の週の設定がデータベースにあるか確認し、なければ設定をつくる
        db.session.add(new_weekly_config) # 作った設定をデータベースに追加
        db.session.commit() # dbにコミット
        return double_point_day # double_point_dayを出力
        
#勉強時間に基づいて計算
def calculate_points(study_minute): 
    today = datetime.utcnow() #本日の日付を取得
    double_point_day = set_or_get_double_point_day() # 今週のポイント2倍dayを取得
    point = study_minute  # 勉強時間に基づくポイント（1分あたり1ポイント
    if today.date() == double_point_day.date(): # もし今日がポイント2倍dayならpoint=*2
        point *= 2
    return point

# テスト
study_minute = 1234  # 例えば、120分勉強した場合
point = calculate_point(study_minute)
print(f"取得ポイント: {point}")

=======
   


>>>>>>> ef898c06fc52f2fe64356e86b2dae5a650ff8c7e
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
<<<<<<< HEAD
        big_reword_arr.append({'name': data.name, 'timestamp': data.timestamp}) # 上に同じ大きなご褒美を取得する
    return render_template('home/index.html', small_reword=small_reword_arr, big_reword=big_reword_arr, double_point_day=double_point_day) # strftime('%A, %B %d, %Y')) 今日が2倍point dayならtopページに表示を行う
=======
        big_reword_arr.append(data.name) # 上に同じ大きなご褒美を取得する
    return render_template('home/index.html', small_reword=small_reword_arr, big_reword=big_reword_arr) # strftime('%A, %B %d, %Y')) 今日が2倍point dayならtopページに表示を行う
>>>>>>> ef898c06fc52f2fe64356e86b2dae5a650ff8c7e

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