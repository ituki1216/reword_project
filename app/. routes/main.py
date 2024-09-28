from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.models import Reword, UserPoints, UserPointsHistory
from app import db
from datetime import datetime, timedelta
import json, random

main_bp = Blueprint('main', __name__, template_folder='../templates/home')

@main_bp.route('/')
@login_required
def home():
    small_reword_arr = []
    big_reword_arr = []
    user_id = current_user.id
    total_points = UserPoints.query.filter_by(user_id=user_id).first()
    small_reword = Reword.query.filter_by(reword_kind=False).all()
    big_reword = Reword.query.filter_by(reword_kind=True).all()
    
    today = datetime.utcnow().date()
    tomorrow = today + timedelta(days=1)
    today_points = UserPointsHistory.query.filter(
        UserPointsHistory.user_id == user_id,
        UserPointsHistory.created_at >= today,
        UserPointsHistory.created_at < tomorrow
    ).first()
    
    for data in small_reword:
        small_reword_arr.append(data.name)
    
    for data in big_reword:
        big_reword_arr.append(data.name)
    
    return render_template(
        'home/index.html', 
        small_reword=json.dumps(small_reword_arr), 
        big_reword=big_reword_arr, 
        today_points=today_points, 
        total_points=total_points
    )

def check_date(user_history):
    today = datetime.utcnow().date()
    if user_history and user_history.created_at.date() == today:
        return True
    return False

@main_bp.route('/stopwatch')
@login_required
def stopwatch():
    user_id = current_user.id
    return render_template('register_rewords/stopwatch.html', user_id=user_id)
