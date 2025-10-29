from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from random import shuffle
from app.models.product import Product
from app.models.category import Category
from app.models.cart import Cart
from app.models.coupon import Coupon
from app.utils.auth import member_login_required

product_bp = Blueprint('product', __name__)

@product_bp.route('/')
def index():
    category_id = request.args.get('category', type=int)
    search = request.args.get('search', '')
    
    # For homepage, show all products without pagination
    products, total = Product.get_all_active(
        category_id=category_id,
        search=search,
        page=1,
        per_page=1000  # Large number to get all products
    )
    
    # Homepage highlight sections
    popular_products = Product.get_top_new(limit=8)
    best_sellers = Product.get_top_best_sellers(limit=8)
    shuffle(popular_products)
    shuffle(best_sellers)
    
    # Only show categories that have products
    categories = Category.get_with_products()
    
    return render_template('shop/index.html', 
                         products=products, 
                         categories=categories,
                         current_category=category_id,
                         search=search,
                         total=total,
                         popular_products=popular_products,
                         best_sellers=best_sellers)

@product_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.get_by_id(product_id)
    if not product:
        flash('商品不存在', 'error')
        return redirect(url_for('product.index'))
    
    # Get related products from same store
    from app.utils.db import get_db_connection
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT p.id, p.name, p.price, p.discount_price, p.image_url
                FROM products p
                WHERE p.store_id = %s AND p.id != %s AND p.status = 'active'
                ORDER BY p.created_at DESC
                LIMIT 4
            """, (product.store_id, product_id))
            related_products = cursor.fetchall()
    finally:
        conn.close()
    
    return render_template('shop/product_detail.html', 
                         product=product, 
                         related_products=related_products)

@product_bp.route('/add_to_cart', methods=['POST'])
@member_login_required
def add_to_cart():
    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', 1, type=int)
    
    if not product_id or quantity <= 0:
        flash('無效的商品或數量', 'error')
        return redirect(url_for('product.index'))
    
    # Check if product exists and is in stock
    product = Product.get_by_id(product_id)
    if not product:
        flash('商品不存在', 'error')
        return redirect(url_for('product.index'))
    
    if not product.is_in_stock():
        flash('商品缺貨', 'error')
        return redirect(url_for('product.product_detail', product_id=product_id))
    
    if quantity > product.stock:
        flash(f'庫存不足，目前庫存：{product.stock}', 'error')
        return redirect(url_for('product.product_detail', product_id=product_id))
    
    success, error = Cart.add_item(session['member_id'], product_id, quantity)
    if success:
        flash('商品已加入購物車', 'success')
    else:
        flash(error, 'error')
    
    return redirect(url_for('product.product_detail', product_id=product_id))

@product_bp.route('/search')
def search():
    search_term = request.args.get('q', '')
    if not search_term:
        return redirect(url_for('product.index'))
    
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)
    
    products, total = Product.get_all_active(
        category_id=category_id,
        search=search_term,
        page=page
    )
    
    categories = Category.get_all()
    
    # Pagination info
    from math import ceil
    total_pages = ceil(total / 12) if total > 0 else 1
    
    return render_template('shop/search.html',
                         products=products,
                         categories=categories,
                         current_category=category_id,
                         search=search_term,
                         page=page,
                         total_pages=total_pages,
                         total=total)
