from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.user import User
from app.models.coupon import Coupon
from app.models.order import Order
from app.models.store import Store
from app.models.product import Product
from app.models.category import Category
from app.utils.auth import admin_login_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
def index():
    """Redirect to dashboard if logged in, otherwise to login"""
    if 'admin_id' in session:
        return redirect(url_for('admin.dashboard'))
    else:
        return redirect(url_for('admin.login'))

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, redirect to dashboard
    if 'admin_id' in session:
        return redirect(url_for('admin.dashboard'))
    
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
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Validate per_page (allow 10, 20, 50, 100)
    allowed_per_page = [10, 20, 50, 100]
    if per_page not in allowed_per_page:
        per_page = 10
    
    from app.utils.db import get_db_connection
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Get total count
            cursor.execute("SELECT COUNT(*) as total FROM users")
            total = cursor.fetchone()['total']
            
            # Get users with pagination
            offset = (page - 1) * per_page
            cursor.execute("""
                SELECT id, username, role, created_at 
                FROM users 
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, (per_page, offset))
            results = cursor.fetchall()
            users = [User(**result) for result in results]
    finally:
        conn.close()
    
    return render_template('admin/users.html', users=users, total=total, page=page, per_page=per_page)

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
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Validate per_page (allow 10, 20, 50, 100)
    allowed_per_page = [10, 20, 50, 100]
    if per_page not in allowed_per_page:
        per_page = 10
    
    # Get all stores (not just active ones) for admin review
    from app.utils.db import get_db_connection
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Get total count
            cursor.execute("SELECT COUNT(*) as total FROM stores")
            total = cursor.fetchone()['total']
            
            # Get stores with pagination
            offset = (page - 1) * per_page
            cursor.execute("""
                SELECT s.id, s.member_id, s.store_name, s.description, s.status, s.created_at, m.name as owner_name 
                FROM stores s 
                JOIN members m ON s.member_id = m.id 
                ORDER BY s.created_at DESC
                LIMIT %s OFFSET %s
            """, (per_page, offset))
            stores = cursor.fetchall()
    finally:
        conn.close()
    
    return render_template('admin/stores.html', stores=stores, total=total, page=page, per_page=per_page)

@admin_bp.route('/approve_store/<int:store_id>')
@admin_login_required
def approve_store(store_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    store = Store.get_by_id(store_id)
    if store:
        if store.update(status='active'):
            flash('商店已啟用', 'success')
        else:
            flash('操作失敗', 'error')
    else:
        flash('商店不存在', 'error')
    
    return redirect(url_for('admin.stores', page=page, per_page=per_page))

@admin_bp.route('/reject_store/<int:store_id>')
@admin_login_required
def reject_store(store_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    store = Store.get_by_id(store_id)
    if store:
        if store.update(status='inactive'):
            flash('商店已停用', 'success')
        else:
            flash('操作失敗', 'error')
    else:
        flash('商店不存在', 'error')
    
    return redirect(url_for('admin.stores', page=page, per_page=per_page))

@admin_bp.route('/coupons')
@admin_login_required
def coupons():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Validate per_page (allow 10, 20, 50, 100)
    allowed_per_page = [10, 20, 50, 100]
    if per_page not in allowed_per_page:
        per_page = 10
    
    from app.utils.db import get_db_connection
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Get total count
            cursor.execute("SELECT COUNT(*) as total FROM coupons")
            total = cursor.fetchone()['total']
            
            # Get coupons with pagination
            offset = (page - 1) * per_page
            cursor.execute("""
                SELECT id, code, discount_type, discount_value, min_purchase, max_discount,
                       valid_from, valid_to, usage_limit, used_count, created_by_type,
                       created_by_id, applicable_to, applicable_id, created_at
                FROM coupons 
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, (per_page, offset))
            results = cursor.fetchall()
            coupons = [Coupon(**result) for result in results]
    finally:
        conn.close()
    
    return render_template('admin/coupons.html', coupons=coupons, total=total, page=page, per_page=per_page)

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
    per_page = request.args.get('per_page', 10, type=int)
    
    # Validate per_page (allow 10, 20, 50, 100)
    allowed_per_page = [10, 20, 50, 100]
    if per_page not in allowed_per_page:
        per_page = 10
    
    # Get orders with member names directly from database
    from app.utils.db import get_db_connection
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Get total count
            cursor.execute("SELECT COUNT(*) as total FROM orders")
            total = cursor.fetchone()['total']
            
            # Get orders with pagination
            offset = (page - 1) * per_page
            cursor.execute("""
                SELECT o.id, o.member_id, o.order_number, o.total_amount, o.discount_amount, 
                       o.final_amount, o.coupon_id, o.status, o.created_at, m.name as member_name
                FROM orders o
                JOIN members m ON o.member_id = m.id
                ORDER BY o.created_at DESC 
                LIMIT %s OFFSET %s
            """, (per_page, offset))
            
            orders = cursor.fetchall()
    finally:
        conn.close()
    
    return render_template('admin/orders.html', orders=orders, total=total, page=page, per_page=per_page)

@admin_bp.route('/products')
@admin_login_required
def products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '').strip()
    
    # Validate per_page (allow 10, 20, 50, 100)
    allowed_per_page = [10, 20, 50, 100]
    if per_page not in allowed_per_page:
        per_page = 10
    
    from app.utils.db import get_db_connection
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Build query with search
            base_query = """
                FROM products p
                LEFT JOIN stores s ON p.store_id = s.id
                LEFT JOIN categories c ON p.category_id = c.id
            """
            where_clause = ""
            params = []
            
            if search:
                where_clause = "WHERE (p.name LIKE %s OR p.description LIKE %s OR s.store_name LIKE %s)"
                search_pattern = f"%{search}%"
                params = [search_pattern, search_pattern, search_pattern]
            
            # Get total count
            count_query = f"SELECT COUNT(*) as total {base_query} {where_clause}"
            cursor.execute(count_query, params)
            total = cursor.fetchone()['total']
            
            # Get products with pagination
            offset = (page - 1) * per_page
            select_query = f"""
                SELECT p.id, p.store_id, p.category_id, p.name, p.description, p.price, p.discount_price,
                       p.stock, p.image_url, p.status, p.created_at, s.store_name, c.name as category_name
                {base_query}
                {where_clause}
                ORDER BY p.created_at DESC
                LIMIT %s OFFSET %s
            """
            params.extend([per_page, offset])
            cursor.execute(select_query, params)
            
            products = cursor.fetchall()
    finally:
        conn.close()
    
    return render_template('admin/products.html', products=products, total=total, page=page, per_page=per_page, search=search)

@admin_bp.route('/products/create', methods=['GET', 'POST'])
@admin_login_required
def create_product():
    if request.method == 'POST':
        store_id = int(request.form.get('store_id', 0))
        category_id = int(request.form.get('category_id', 0))
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price = float(request.form.get('price', 0))
        discount_price = float(request.form.get('discount_price', 0)) if request.form.get('discount_price') else None
        stock = int(request.form.get('stock', 0))
        status = request.form.get('status', 'active')
        image_file = request.files.get('image')
        
        if not all([store_id, category_id, name, price]):
            flash('請填寫所有必填欄位', 'error')
            # Get stores and categories for retry
            from app.utils.db import get_db_connection
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT id, store_name FROM stores WHERE status = 'active' ORDER BY store_name")
                    stores = cursor.fetchall()
                    cursor.execute("SELECT id, name FROM categories ORDER BY name")
                    categories = cursor.fetchall()
            finally:
                conn.close()
            return render_template('admin/create_product.html', stores=stores, categories=categories)
        
        product, error = Product.create(
            store_id=store_id,
            category_id=category_id,
            name=name,
            description=description,
            price=price,
            discount_price=discount_price,
            stock=stock,
            image_file=image_file
        )
        
        if product:
            # Update status if needed
            if status != 'active':
                product.update(status=status)
            flash('商品創建成功', 'success')
            return redirect(url_for('admin.products'))
        else:
            flash(error or '商品創建失敗', 'error')
    
    # Get all stores and categories for dropdown
    from app.utils.db import get_db_connection
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, store_name FROM stores WHERE status = 'active' ORDER BY store_name")
            stores = cursor.fetchall()
            cursor.execute("SELECT id, name FROM categories ORDER BY name")
            categories = cursor.fetchall()
    finally:
        conn.close()
    
    return render_template('admin/create_product.html', stores=stores, categories=categories)

@admin_bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@admin_login_required
def edit_product(product_id):
    product = Product.get_by_id(product_id)
    if not product:
        flash('商品不存在', 'error')
        return redirect(url_for('admin.products'))
    
    if request.method == 'POST':
        store_id = int(request.form.get('store_id', 0))
        category_id = int(request.form.get('category_id', 0))
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price = float(request.form.get('price', 0))
        discount_price = float(request.form.get('discount_price', 0)) if request.form.get('discount_price') else None
        stock = int(request.form.get('stock', 0))
        status = request.form.get('status', 'active')
        image_file = request.files.get('image')
        
        if not all([store_id, category_id, name, price]):
            flash('請填寫所有必填欄位', 'error')
            from app.utils.db import get_db_connection
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT id, store_name FROM stores WHERE status = 'active' ORDER BY store_name")
                    stores = cursor.fetchall()
                    cursor.execute("SELECT id, name FROM categories ORDER BY name")
                    categories = cursor.fetchall()
            finally:
                conn.close()
            return render_template('admin/edit_product.html', product=product, stores=stores, categories=categories)
        
        if product.update(
            name=name,
            description=description,
            price=price,
            discount_price=discount_price,
            stock=stock,
            category_id=category_id,
            status=status,
            image_file=image_file
        ):
            flash('商品更新成功', 'success')
            return redirect(url_for('admin.products'))
        else:
            flash('商品更新失敗', 'error')
    
    # Get all stores and categories for dropdown
    from app.utils.db import get_db_connection
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, store_name FROM stores WHERE status = 'active' ORDER BY store_name")
            stores = cursor.fetchall()
            cursor.execute("SELECT id, name FROM categories ORDER BY name")
            categories = cursor.fetchall()
    finally:
        conn.close()
    
    return render_template('admin/edit_product.html', product=product, stores=stores, categories=categories)

@admin_bp.route('/products/<int:product_id>/delete', methods=['POST'])
@admin_login_required
def delete_product(product_id):
    product = Product.get_by_id(product_id)
    if not product:
        flash('商品不存在', 'error')
        return redirect(url_for('admin.products'))
    
    if product.delete():
        flash('商品已刪除', 'success')
    else:
        flash('商品刪除失敗', 'error')
    
    return redirect(url_for('admin.products'))
