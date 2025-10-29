from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.coupon import Coupon
from app.utils.auth import member_login_required

coupon_bp = Blueprint('coupon', __name__)

@coupon_bp.route('/validate', methods=['POST'])
@member_login_required
def validate_coupon():
    coupon_code = request.form.get('coupon_code', '').strip()
    total_amount = float(request.form.get('total_amount', 0))
    product_ids = request.form.getlist('product_ids', type=int)
    store_id = request.form.get('store_id', type=int)
    
    if not coupon_code:
        return {'valid': False, 'message': '請輸入優惠券代碼'}
    
    coupon = Coupon.get_by_code(coupon_code)
    if not coupon:
        return {'valid': False, 'message': '優惠券不存在'}
    
    is_valid, message = coupon.is_valid(total_amount, product_ids, store_id)
    if is_valid:
        discount_amount = coupon.calculate_discount(total_amount)
        return {
            'valid': True, 
            'message': '優惠券有效',
            'discount_amount': discount_amount,
            'final_amount': total_amount - discount_amount
        }
    else:
        return {'valid': False, 'message': message}
