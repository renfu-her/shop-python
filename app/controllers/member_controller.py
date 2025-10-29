from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.member import Member
from app.models.store import Store
from app.utils.auth import member_login_required

member_bp = Blueprint('member', __name__)

@member_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('請填寫所有欄位', 'error')
            return render_template('member/login.html')
        
        member = Member.get_by_email(email)
        if member and member.check_password(password):
            session['member_id'] = member.id
            session['member_name'] = member.name
            flash(f'歡迎回來，{member.name}！', 'success')
            return redirect(url_for('product.index'))
        else:
            flash('電子郵件或密碼錯誤', 'error')
    
    return render_template('member/login.html')

@member_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        phone = request.form.get('phone')
        
        # Validation
        if not all([name, email, password, confirm_password]):
            flash('請填寫所有必填欄位', 'error')
            return render_template('member/register.html')
        
        if password != confirm_password:
            flash('密碼確認不符', 'error')
            return render_template('member/register.html')
        
        if len(password) < 6:
            flash('密碼長度至少6個字元', 'error')
            return render_template('member/register.html')
        
        # Create member
        member, error = Member.create(email, password, name, phone)
        if member:
            flash('註冊成功！請登入', 'success')
            return redirect(url_for('member.login'))
        else:
            flash(error, 'error')
    
    return render_template('member/register.html')

@member_bp.route('/logout')
def logout():
    session.pop('member_id', None)
    session.pop('member_name', None)
    flash('已登出', 'info')
    return redirect(url_for('product.index'))

@member_bp.route('/profile')
@member_login_required
def profile():
    member = Member.get_by_id(session['member_id'])
    return render_template('member/profile.html', member=member)

@member_bp.route('/profile/edit', methods=['GET', 'POST'])
@member_login_required
def edit_profile():
    member = Member.get_by_id(session['member_id'])
    
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        
        if member.update_profile(name, phone):
            session['member_name'] = name
            flash('個人資料更新成功', 'success')
            return redirect(url_for('member.profile'))
        else:
            flash('更新失敗，請重試', 'error')
    
    return render_template('member/edit_profile.html', member=member)

@member_bp.route('/my_stores')
@member_login_required
def my_stores():
    stores = Store.get_by_member(session['member_id'])
    return render_template('member/my_stores.html', stores=stores)

@member_bp.route('/create_store', methods=['GET', 'POST'])
@member_login_required
def create_store():
    if request.method == 'POST':
        store_name = request.form.get('store_name')
        description = request.form.get('description')
        
        if not store_name:
            flash('請輸入商店名稱', 'error')
            return render_template('member/create_store.html')
        
        store, error = Store.create(session['member_id'], store_name, description)
        if store:
            flash('商店創建成功，等待審核', 'success')
            return redirect(url_for('member.my_stores'))
        else:
            flash(error, 'error')
    
    return render_template('member/create_store.html')
