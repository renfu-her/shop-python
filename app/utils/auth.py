from functools import wraps
from flask import session, redirect, url_for, flash, request

def member_login_required(f):
    """Decorator to require member login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'member_id' not in session:
            flash('請先登入會員', 'warning')
            return redirect(url_for('member.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_login_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('請先登入管理員', 'warning')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

def store_owner_required(f):
    """Decorator to require store ownership"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'member_id' not in session:
            flash('請先登入會員', 'warning')
            return redirect(url_for('member.login'))
        
        # Check if user owns the store
        store_id = kwargs.get('store_id')
        if store_id:
            from app.utils.db import get_db_connection
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT id FROM stores WHERE id = %s AND member_id = %s",
                        (store_id, session['member_id'])
                    )
                    if not cursor.fetchone():
                        flash('您沒有權限管理此商店', 'error')
                        return redirect(url_for('store.my_stores'))
            finally:
                conn.close()
        
        return f(*args, **kwargs)
    return decorated_function
