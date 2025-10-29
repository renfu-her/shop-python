from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.store import Store
from app.models.product import Product
from app.models.coupon import Coupon
from app.models.order import Order
from app.utils.auth import member_login_required, store_owner_required

store_bp = Blueprint('store', __name__)

@store_bp.route('/dashboard/<int:store_id>')
@member_login_required
@store_owner_required
def dashboard(store_id):
    store = Store.get_by_id(store_id)
    if not store:
        flash('商店不存在', 'error')
        return redirect(url_for('member.my_stores'))
    
    # Get store statistics
    stats = store.get_stats()
    
    # Get recent orders
    orders, _ = Order.get_by_store(store_id, page=1, per_page=5)
    
    # Get recent products
    products = Product.get_by_store(store_id)[:5]
    
    return render_template('store/dashboard.html', store=store, stats=stats, orders=orders, products=products)

@store_bp.route('/products/<int:store_id>')
@member_login_required
@store_owner_required
def products(store_id):
    store = Store.get_by_id(store_id)
    if not store:
        flash('商店不存在', 'error')
        return redirect(url_for('member.my_stores'))
    
    products = Product.get_by_store(store_id)
    return render_template('store/products.html', store=store, products=products)

@store_bp.route('/add_product/<int:store_id>', methods=['GET', 'POST'])
@member_login_required
@store_owner_required
def add_product(store_id):
    store = Store.get_by_id(store_id)
    if not store:
        flash('商店不存在', 'error')
        return redirect(url_for('member.my_stores'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        category_id = int(request.form.get('category_id', 0))
        price = float(request.form.get('price', 0))
        discount_price = float(request.form.get('discount_price', 0)) if request.form.get('discount_price') else None
        stock = int(request.form.get('stock', 0))
        image_file = request.files.get('image')
        
        if not all([name, category_id, price]):
            flash('請填寫所有必填欄位', 'error')
            return render_template('store/add_product.html', store=store)
        
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
            flash('商品添加成功', 'success')
            return redirect(url_for('store.products', store_id=store_id))
        else:
            flash(error, 'error')
    
    from app.models.category import Category
    categories = Category.get_all()
    return render_template('store/add_product.html', store=store, categories=categories)

@store_bp.route('/edit_product/<int:store_id>/<int:product_id>', methods=['GET', 'POST'])
@member_login_required
@store_owner_required
def edit_product(store_id, product_id):
    store = Store.get_by_id(store_id)
    if not store:
        flash('商店不存在', 'error')
        return redirect(url_for('member.my_stores'))
    
    product = Product.get_by_id(product_id)
    if not product or product.store_id != store_id:
        flash('商品不存在', 'error')
        return redirect(url_for('store.products', store_id=store_id))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        category_id = int(request.form.get('category_id', 0))
        price = float(request.form.get('price', 0))
        discount_price = float(request.form.get('discount_price', 0)) if request.form.get('discount_price') else None
        stock = int(request.form.get('stock', 0))
        status = request.form.get('status', 'active')
        image_file = request.files.get('image')
        
        if not all([name, category_id, price]):
            flash('請填寫所有必填欄位', 'error')
            return render_template('store/edit_product.html', store=store, product=product)
        
        if product.update(name=name, description=description, category_id=category_id,
                         price=price, discount_price=discount_price, stock=stock,
                         status=status, image_file=image_file):
            flash('商品更新成功', 'success')
            return redirect(url_for('store.products', store_id=store_id))
        else:
            flash('更新失敗，請重試', 'error')
    
    from app.models.category import Category
    categories = Category.get_all()
    return render_template('store/edit_product.html', store=store, product=product, categories=categories)

@store_bp.route('/delete_product/<int:store_id>/<int:product_id>')
@member_login_required
@store_owner_required
def delete_product(store_id, product_id):
    store = Store.get_by_id(store_id)
    if not store:
        flash('商店不存在', 'error')
        return redirect(url_for('member.my_stores'))
    
    product = Product.get_by_id(product_id)
    if not product or product.store_id != store_id:
        flash('商品不存在', 'error')
        return redirect(url_for('store.products', store_id=store_id))
    
    if product.delete():
        flash('商品刪除成功', 'success')
    else:
        flash('刪除失敗，請重試', 'error')
    
    return redirect(url_for('store.products', store_id=store_id))

@store_bp.route('/orders/<int:store_id>')
@member_login_required
@store_owner_required
def orders(store_id):
    store = Store.get_by_id(store_id)
    if not store:
        flash('商店不存在', 'error')
        return redirect(url_for('member.my_stores'))
    
    page = request.args.get('page', 1, type=int)
    orders, total = Order.get_by_store(store_id, page=page)
    return render_template('store/orders.html', store=store, orders=orders, total=total, page=page)

@store_bp.route('/update_order_status/<int:store_id>/<int:order_id>', methods=['POST'])
@member_login_required
@store_owner_required
def update_order_status(store_id, order_id):
    store = Store.get_by_id(store_id)
    if not store:
        flash('商店不存在', 'error')
        return redirect(url_for('member.my_stores'))
    
    order = Order.get_by_id(order_id)
    if not order:
        flash('訂單不存在', 'error')
        return redirect(url_for('store.orders', store_id=store_id))
    
    new_status = request.form.get('status')
    if order.update_status(new_status):
        flash('訂單狀態更新成功', 'success')
    else:
        flash('更新失敗，請重試', 'error')
    
    return redirect(url_for('store.orders', store_id=store_id))

@store_bp.route('/coupons/<int:store_id>')
@member_login_required
@store_owner_required
def coupons(store_id):
    store = Store.get_by_id(store_id)
    if not store:
        flash('商店不存在', 'error')
        return redirect(url_for('member.my_stores'))
    
    coupons = Coupon.get_by_creator('store', store_id)
    return render_template('store/coupons.html', store=store, coupons=coupons)

@store_bp.route('/create_coupon/<int:store_id>', methods=['GET', 'POST'])
@member_login_required
@store_owner_required
def create_coupon(store_id):
    store = Store.get_by_id(store_id)
    if not store:
        flash('商店不存在', 'error')
        return redirect(url_for('member.my_stores'))
    
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
            return render_template('store/create_coupon.html', store=store)
        
        from datetime import datetime
        valid_from = datetime.fromisoformat(valid_from)
        valid_to = datetime.fromisoformat(valid_to)
        
        coupon, error = Coupon.create(
            code=code, discount_type=discount_type, discount_value=discount_value,
            min_purchase=min_purchase, max_discount=max_discount,
            valid_from=valid_from, valid_to=valid_to, usage_limit=usage_limit,
            created_by_type='store', created_by_id=store_id,
            applicable_to=applicable_to, applicable_id=applicable_id
        )
        
        if coupon:
            flash('優惠券創建成功', 'success')
            return redirect(url_for('store.coupons', store_id=store_id))
        else:
            flash(error, 'error')
    
    return render_template('store/create_coupon.html', store=store)
