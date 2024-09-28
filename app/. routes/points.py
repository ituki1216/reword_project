from flask import Blueprint, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import UserPoints, UserPointsHistory
from app import db
import logging
from datetime import datetime, timedelta

points_bp = Blueprint('points', __name__)

@points_bp.route('/add_points', methods=['POST'])
@login_required
def add_points():
    user_id = current_user.id
    user = UserPoints.query.filter_by(user_id=user_id).first()
    if not user:
        user = UserPoints(user_id=user_id, points=0)
        db.session.add(user)
        db.session.commit()
    
    today = datetime.utcnow().date()
    tomorrow = today + timedelta(days=1)
    user_history = UserPointsHistory.query.filter(
        UserPointsHistory.user_id == user_id,
        UserPointsHistory.created_at >= today,
        UserPointsHistory.created_at < tomorrow
    ).first()
    
    if user_history is None:
        user_history = UserPointsHistory(user_id=user_id, points=1)
        db.session.add(user_history)
    else:
        if user_history.created_at.date() == today:
            user_history.points += 1
        else:
            user_history.points = 1  # 新しい日にリセット
    user.points += 1  # 1ポイントを加算
    db.session.commit()
    return jsonify({'points': user.points})
    
@points_bp.route('/get_points', methods=['GET'])
@login_required
def get_points():
    user_id = current_user.id
    user = UserPoints.query.filter_by(user_id=user_id).first()
    if user is None:
        user = UserPoints(user_id=user_id, points=0)
        db.session.add(user)
        db.session.commit()
    return jsonify({'points': user.points})


logger = logging.getLogger(__name__)

@points_bp.route('/test_points', methods=['POST'])
def test_add_points():
    try:
        user_id = current_user.id
        user = UserPoints.query.filter_by(user_id=user_id).first()
        if not user:
            user = UserPoints(user_id=user_id, points=1000)
            db.session.add(user)
        else:
            user.points += 1000
        db.session.commit()
        logger.info(f"ポイントが付与されました。現在のポイント: {user.points}")
        flash("1000ポイントを付与しました。", "success")
    except Exception as e:
        logger.error(f"ポイント付与中にエラーが発生しました: {e}")
        flash('ポイントの付与に失敗しました。再度お試しください。', 'danger')
    finally:
        return redirect(url_for('main.home'))

