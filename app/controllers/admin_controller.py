from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.user import User
from app.models.coupon import Coupon
from app.models.order import Order
from app.models.store import Store
from app.utils.auth import admin_login_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('請填寫所有欄位', 'error')
            return render_template('admin/login.html')
        
        user = User.get_by_username(username)
        if user and user.check_password(password):
            session['admin_id'] = user.id
            session['admin_username'] = user.username
            session['admin_role'] = user.role
            flash(f'歡迎回來，{user.username}！', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('使用者名稱或密碼錯誤', 'error')
    
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    session.pop('admin_role', None)
    flash('已登出', 'info')
    return redirect(url_for('admin.login'))

@admin_bp.route('/dashboard')
@admin_login_required
def dashboard():
    # Get statistics
    from app.utils.db import get_db_connection
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Total members
            cursor.execute("SELECT COUNT(*) as count FROM members")
            total_members = cursor.fetchone()['count']
            
            # Total stores
            cursor.execute("SELECT COUNT(*) as count FROM stores")
            total_stores = cursor.fetchone()['count']
            
            # Active stores
            cursor.execute("SELECT COUNT(*) as count FROM stores WHERE status = 'active'")
            active_stores = cursor.fetchone()['count']
            
            # Total products
            cursor.execute("SELECT COUNT(*) as count FROM products WHERE status = 'active'")
            total_products = cursor.fetchone()['count']
            
            # Total orders
            cursor.execute("SELECT COUNT(*) as count FROM orders")
            total_orders = cursor.fetchone()['count']
            
            # Total revenue
            cursor.execute("SELECT COALESCE(SUM(final_amount), 0) as revenue FROM orders WHERE status != 'cancelled'")
            total_revenue = cursor.fetchone()['revenue']
            
            # Recent orders
            cursor.execute("""
                SELECT o.id, o.order_number, o.final_amount, o.status, o.created_at, m.name as member_name
                FROM orders o
                JOIN members m ON o.member_id = m.id
                ORDER BY o.created_at DESC
                LIMIT 5
            """)
            recent_orders = cursor.fetchall()
            
            stats = {
                'total_members': total_members,
                'total_stores': total_stores,
                'active_stores': active_stores,
                'total_products': total_products,
                'total_orders': total_orders,
                'total_revenue': total_revenue,
                'recent_orders': recent_orders
            }
            
    finally:
        conn.close()
    
    return render_template('admin/dashboard.html', stats=stats)

@admin_bp.route('/users')
@admin_login_required
def users():
    users = User.get_all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/create_user', methods=['GET', 'POST'])
@admin_login_required
def create_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'admin')
        
        if not username or not password:
            flash('請填寫所有欄位', 'error')
            return render_template('admin/create_user.html')
        
        user, error = User.create(username, password, role)
        if user:
            flash('使用者創建成功', 'success')
            return redirect(url_for('admin.users'))
        else:
            flash(error, 'error')
    
    return render_template('admin/create_user.html')

@admin_bp.route('/stores')
@admin_login_required
def stores():
    stores = Store.get_all_active()
    return render_template('admin/stores.html', stores=stores)

@admin_bp.route('/approve_store/<int:store_id>')
@admin_login_required
def approve_store(store_id):
    store = Store.get_by_id(store_id)
    if store:
        if store.update(status='active'):
            flash('商店已啟用', 'success')
        else:
            flash('操作失敗', 'error')
    else:
        flash('商店不存在', 'error')
    
    return redirect(url_for('admin.stores'))

@admin_bp.route('/reject_store/<int:store_id>')
@admin_login_required
def reject_store(store_id):
    store = Store.get_by_id(store_id)
    if store:
        if store.update(status='inactive'):
            flash('商店已停用', 'success')
        else:
            flash('操作失敗', 'error')
    else:
        flash('商店不存在', 'error')
    
    return redirect(url_for('admin.stores'))

@admin_bp.route('/coupons')
@admin_login_required
def coupons():
    coupons = Coupon.get_all()
    return render_template('admin/coupons.html', coupons=coupons)

@admin_bp.route('/create_coupon', methods=['GET', 'POST'])
@admin_login_required
def create_coupon():
    if request.method == 'POST':
        code = request.form.get('code')
        discount_type = request.form.get('discount_type')
        discount_value = float(request.form.get('discount_value', 0))
        min_purchase = float(request.form.get('min_purchase', 0))
        max_discount = float(request.form.get('max_discount', 0)) if request.form.get('max_discount') else None
        valid_from = request.form.get('valid_from')
        valid_to = request.form.get('valid_to')
        usage_limit = int(request.form.get('usage_limit', 0)) if request.form.get('usage_limit') else None
        applicable_to = request.form.get('applicable_to', 'all')
        applicable_id = int(request.form.get('applicable_id', 0)) if request.form.get('applicable_id') else None
        
        if not all([code, discount_type, discount_value, valid_from, valid_to]):
            flash('請填寫所有必填欄位', 'error')
            return render_template('admin/create_coupon.html')
        
        from datetime import datetime
        valid_from = datetime.fromisoformat(valid_from)
        valid_to = datetime.fromisoformat(valid_to)
        
        coupon, error = Coupon.create(
            code=code, discount_type=discount_type, discount_value=discount_value,
            min_purchase=min_purchase, max_discount=max_discount,
            valid_from=valid_from, valid_to=valid_to, usage_limit=usage_limit,
            created_by_type='admin', created_by_id=session['admin_id'],
            applicable_to=applicable_to, applicable_id=applicable_id
        )
        
        if coupon:
            flash('優惠券創建成功', 'success')
            return redirect(url_for('admin.coupons'))
        else:
            flash(error, 'error')
    
    return render_template('admin/create_coupon.html')

@admin_bp.route('/orders')
@admin_login_required
def orders():
    page = request.args.get('page', 1, type=int)
    orders, total = Order.get_all(page=page)
    return render_template('admin/orders.html', orders=orders, total=total, page=page)
