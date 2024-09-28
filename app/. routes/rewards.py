from flask import Blueprint, render_template, redirect, request, jsonify
from flask_login import login_required, current_user
from app.models import Reword, UserPoints
from app import db
from flask import Flask, jsonify, render_template, flash, url_for

import random



rewards_bp = Blueprint('rewards', __name__, template_folder='../templates/register_rewords')

@rewards_bp.route('/small_reword', methods=['GET'])
@login_required
def get_small_reword():
    user_id = current_user.id
    rewords = []
    user_points = UserPoints.query.filter_by(user_id=user_id).first()
    small_reword = Reword.query.filter_by(reword_kind=False, user_id=user_id).all()
    
    for reword in small_reword:
        if user_points and user_points.points >= reword.point:
            rewords.append(reword.name)
    
    if rewords:
        select_reword = random.choice(rewords)
        selected_reword = Reword.query.filter_by(reword_kind=False, user_id=user_id, name=select_reword).first()
        if selected_reword:
            user_points.points -= selected_reword.point
            db.session.commit()
            return jsonify({'reword': select_reword})
    return jsonify([])

@rewards_bp.route('/big_reword', methods=['GET'])
@login_required
def get_big_reword():
    user_id = current_user.id
    rewords = []
    user_points = UserPoints.query.filter_by(user_id=user_id).first()
    big_reword = Reword.query.filter_by(reword_kind=True, user_id=user_id).all()
    
    for reword in big_reword:
        if user_points and user_points.points >= reword.point:
            rewords.append(reword.name)
    
    if rewords:
        select_reword = random.choice(rewords)
        selected_reword = Reword.query.filter_by(reword_kind=True, user_id=user_id, name=select_reword).first()
        if selected_reword:
            user_points.points -= selected_reword.point
            db.session.commit()
            return jsonify({'reword': select_reword})
    return jsonify([])

rewards_bp = Blueprint('rewards', __name__, template_folder='../templates/register_rewords')

@rewards_bp.route('/small_reword', methods=['GET'])
@login_required
def get_small_reword():
    user_id = current_user.id
    rewords = []
    user_points = UserPoints.query.filter_by(user_id=user_id).first()
    small_reword = Reword.query.filter_by(reword_kind=False, user_id=user_id).all()
    
    for reword in small_reword:
        if user_points and user_points.points >= reword.point:
            rewords.append(reword.name)
    
    if rewords:
        select_reword = random.choice(rewords)
        selected_reword = Reword.query.filter_by(reword_kind=False, user_id=user_id, name=select_reword).first()
        if selected_reword:
            user_points.points -= selected_reword.point
            db.session.commit()
            return jsonify({'reword': select_reword})
    return jsonify([])

@rewards_bp.route('/big_reword', methods=['GET'])
@login_required
def get_big_reword():
    user_id = current_user.id
    rewords = []
    user_points = UserPoints.query.filter_by(user_id=user_id).first()
    big_reword = Reword.query.filter_by(reword_kind=True, user_id=user_id).all()
    
    for reword in big_reword:
        if user_points and user_points.points >= reword.point:
            rewords.append(reword.name)
    
    if rewords:
        select_reword = random.choice(rewords)
        selected_reword = Reword.query.filter_by(reword_kind=True, user_id=user_id, name=select_reword).first()
        if selected_reword:
            user_points.points -= selected_reword.point
            db.session.commit()
            return jsonify({'reword': select_reword})
    return jsonify([])

@rewards_bp.route('/add', methods=['GET'])
@login_required
def add_get():
    small_reword = Reword.query.filter_by(reword_kind=False, user_id=current_user.id).all()
    big_reword = Reword.query.filter_by(reword_kind=True, user_id=current_user.id).all()
    return render_template('register_rewords/index.html', small_reword=small_reword, big_reword=big_reword)

@rewards_bp.route('/create', methods=['POST'])
@login_required
def create_reword():
    reword_kind = False
    if request.form.get('reword_kind') is not None:
        reword_kind = True
        points = random.randint(1, 2)
    else:
        reword_kind = False
        points = random.randint(3, 5)
    reword_text = request.form.get('reword')
    user_id = current_user.id
    new_reword = Reword(
        name=reword_text, 
        reword_kind=reword_kind, 
        user_id=user_id, 
        point=points
    )
    db.session.add(new_reword)
    db.session.commit()
    return redirect(url_for('rewards.add_get'))

@rewards_bp.route('/update', methods=['POST'])
@login_required
def update_reword():
    reword_id = request.form.get("id")
    name = request.form.get("reword")
    reword = Reword.query.filter_by(id=reword_id, user_id=current_user.id).first()
    if reword:
        reword.name = name
        db.session.commit()
        flash('リワードが更新されました。', 'success')
    else:
        flash('リワードが見つかりませんでした。', 'danger')
    return redirect(url_for('rewards.add_get'))

@rewards_bp.route('/delete', methods=['POST'])
@login_required
def delete_reword():
    reword_id = request.form.get("id")
    reword = Reword.query.filter_by(id=reword_id, user_id=current_user.id).first()
    if reword:
        db.session.delete(reword)
        db.session.commit()
        flash('リワードが削除されました。', 'success')
    else:
        flash('リワードが見つかりませんでした。', 'danger')
    return redirect(url_for('rewards.add_get'))
