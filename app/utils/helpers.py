from datetime import datetime
import os
from werkzeug.utils import secure_filename

def format_price(price):
    """Format price with currency symbol"""
    return f"${price:,.0f}"

def format_datetime(dt):
    """Format datetime for display"""
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    return dt.strftime('%Y-%m-%d %H:%M')

def allowed_file(filename):
    """Check if file extension is allowed"""
    from flask import current_app
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_product_image(file, product_id):
    """Save uploaded product image"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add product_id to filename to avoid conflicts
        name, ext = os.path.splitext(filename)
        filename = f"product_{product_id}_{name}{ext}"
        
        from flask import current_app
        upload_folder = current_app.config['UPLOAD_FOLDER']
        
        # Create directory if it doesn't exist
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        return f"images/products/{filename}"
    return None

def generate_order_number():
    """Generate unique order number"""
    import random
    import string
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"ORD{timestamp}{random_str}"

def calculate_discount(price, discount_type, discount_value, max_discount=None):
    """Calculate discount amount"""
    if discount_type == 'percentage':
        discount_amount = price * (discount_value / 100)
        if max_discount and discount_amount > max_discount:
            discount_amount = max_discount
    else:  # fixed amount
        discount_amount = min(discount_value, price)
    
    return discount_amount
