from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.cart import Cart
from app.models.coupon import Coupon
from app.utils.auth import member_login_required

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/')
@member_login_required
def view_cart():
    cart_items = Cart.get_by_member(session['member_id'])
    return render_template('cart/view.html', cart_items=cart_items)

@cart_bp.route('/update_quantity', methods=['POST'])
@member_login_required
def update_quantity():
    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', 0, type=int)
    
    if not product_id:
        flash('無效的商品', 'error')
        return redirect(url_for('cart.view_cart'))
    
    success, error = Cart.update_quantity(session['member_id'], product_id, quantity)
    if success:
        flash('購物車已更新', 'success')
    else:
        flash(error, 'error')
    
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/remove_item', methods=['POST'])
@member_login_required
def remove_item():
    product_id = request.form.get('product_id', type=int)
    
    if not product_id:
        flash('無效的商品', 'error')
        return redirect(url_for('cart.view_cart'))
    
    success, error = Cart.remove_item(session['member_id'], product_id)
    if success:
        flash('商品已從購物車移除', 'success')
    else:
        flash(error, 'error')
    
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/checkout')
@member_login_required
def checkout():
    cart_summary = Cart.get_cart_summary(session['member_id'])
    
    if not cart_summary['items']:
        flash('購物車是空的', 'warning')
        return redirect(url_for('product.index'))
    
    # Get available coupons
    coupons = Coupon.get_all()
    
    return render_template('cart/checkout.html', 
                         cart_summary=cart_summary, 
                         coupons=coupons)

@cart_bp.route('/apply_coupon', methods=['POST'])
@member_login_required
def apply_coupon():
    coupon_code = request.form.get('coupon_code', '').strip()
    
    if not coupon_code:
        flash('請輸入優惠券代碼', 'error')
        return redirect(url_for('cart.checkout'))
    
    cart_summary = Cart.get_cart_summary(session['member_id'])
    if not cart_summary['items']:
        flash('購物車是空的', 'warning')
        return redirect(url_for('product.index'))
    
    coupon = Coupon.get_by_code(coupon_code)
    if not coupon:
        flash('優惠券不存在', 'error')
        return redirect(url_for('cart.checkout'))
    
    # Validate coupon
    product_ids = [item['product_id'] for item in cart_summary['items']]
    store_id = cart_summary['items'][0]['store_id'] if cart_summary['items'] else None
    
    is_valid, message = coupon.is_valid(cart_summary['total_amount'], product_ids, store_id)
    if not is_valid:
        flash(message, 'error')
        return redirect(url_for('cart.checkout'))
    
    # Calculate discount
    discount_amount = coupon.calculate_discount(cart_summary['total_amount'])
    final_amount = cart_summary['total_amount'] - discount_amount
    
    return render_template('cart/checkout.html',
                         cart_summary=cart_summary,
                         applied_coupon=coupon,
                         discount_amount=discount_amount,
                         final_amount=final_amount)
