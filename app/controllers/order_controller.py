from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.order import Order
from app.models.cart import Cart
from app.models.coupon import Coupon
from app.utils.auth import member_login_required

order_bp = Blueprint('order', __name__)

@order_bp.route('/create', methods=['POST'])
@member_login_required
def create_order():
    coupon_code = request.form.get('coupon_code', '').strip()
    
    # Get cart items
    cart_summary = Cart.get_cart_summary(session['member_id'])
    if not cart_summary['items']:
        flash('購物車是空的', 'warning')
        return redirect(url_for('product.index'))
    
    # Prepare cart items for order creation
    cart_items = []
    for item in cart_summary['items']:
        cart_items.append({
            'product_id': item['product_id'],
            'quantity': item['quantity'],
            'price': item['price'],
            'subtotal': item['subtotal'],
            'store_id': item['store_id']
        })
    
    # Create order
    order, error = Order.create(session['member_id'], cart_items, coupon_code)
    if order:
        flash('訂單創建成功！', 'success')
        return redirect(url_for('order.order_detail', order_id=order.id))
    else:
        flash(error, 'error')
        return redirect(url_for('cart.checkout'))

@order_bp.route('/my_orders')
@member_login_required
def my_orders():
    page = request.args.get('page', 1, type=int)
    orders, total = Order.get_by_member(session['member_id'], page=page)
    
    # Pagination info
    from math import ceil
    total_pages = ceil(total / 10) if total > 0 else 1
    
    return render_template('order/my_orders.html', 
                         orders=orders, 
                         page=page,
                         total_pages=total_pages,
                         total=total)

@order_bp.route('/order/<int:order_id>')
@member_login_required
def order_detail(order_id):
    order = Order.get_by_id(order_id)
    if not order or order.member_id != session['member_id']:
        flash('訂單不存在', 'error')
        return redirect(url_for('order.my_orders'))
    
    order_items = order.get_items()
    
    # Get coupon info if applied
    coupon = None
    if order.coupon_id:
        coupon = Coupon.get_by_id(order.coupon_id)
    
    return render_template('order/order_detail.html', 
                         order=order, 
                         order_items=order_items,
                         coupon=coupon)

@order_bp.route('/cancel/<int:order_id>')
@member_login_required
def cancel_order(order_id):
    order = Order.get_by_id(order_id)
    if not order or order.member_id != session['member_id']:
        flash('訂單不存在', 'error')
        return redirect(url_for('order.my_orders'))
    
    if order.status != 'pending':
        flash('只能取消待處理的訂單', 'error')
        return redirect(url_for('order.order_detail', order_id=order_id))
    
    if order.update_status('cancelled'):
        flash('訂單已取消', 'success')
    else:
        flash('取消失敗，請重試', 'error')
    
    return redirect(url_for('order.order_detail', order_id=order_id))
