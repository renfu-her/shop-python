from datetime import datetime
import os
from werkzeug.utils import secure_filename

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

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
    """Save uploaded product image and convert to WebP format"""
    if file and allowed_file(file.filename):
        from flask import current_app
        upload_folder = current_app.config['UPLOAD_FOLDER']
        
        # Create directory if it doesn't exist
        os.makedirs(upload_folder, exist_ok=True)
        
        # Generate filename with product_id
        name = secure_filename(file.filename)
        name_without_ext = os.path.splitext(name)[0]
        file_ext = os.path.splitext(name)[1].lower()
        
        # If already WebP, keep it as WebP; otherwise convert to WebP
        if file_ext == '.webp':
            filename = f"product_{product_id}_{name_without_ext}.webp"
        else:
            filename = f"product_{product_id}_{name_without_ext}.webp"
        
        file_path = os.path.join(upload_folder, filename)
        
        try:
            # Open image using Pillow
            if PIL_AVAILABLE:
                # Reset file pointer to beginning
                file.seek(0)
                img = Image.open(file.stream)
                
                # If already WebP and same format, we can optimize it
                if file_ext == '.webp' and img.format == 'WEBP':
                    # Re-optimize existing WebP
                    img.save(file_path, 'WEBP', quality=85, optimize=True)
                else:
                    # Handle animated GIFs - take first frame
                    if hasattr(img, 'is_animated') and img.is_animated:
                        img.seek(0)  # Get first frame
                    
                    # Convert to RGB if needed (WebP supports RGBA, but we'll use RGB for consistency)
                    if img.mode in ('RGBA', 'LA'):
                        # Create a white background for transparency
                        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'LA':
                            img = img.convert('RGBA')
                        rgb_img.paste(img, mask=img.split()[-1])
                        img = rgb_img
                    elif img.mode == 'P':
                        # Palette mode (like some GIFs)
                        if 'transparency' in img.info:
                            img = img.convert('RGBA')
                            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                            rgb_img.paste(img, mask=img.split()[-1])
                            img = rgb_img
                        else:
                            img = img.convert('RGB')
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Save as WebP with quality optimization
                    img.save(file_path, 'WEBP', quality=85, optimize=True)
                
                return f"images/products/{filename}"
            else:
                # Fallback: save original file if Pillow is not available
                file.seek(0)  # Reset file pointer
                original_ext = os.path.splitext(name)[1]
                filename = f"product_{product_id}_{name_without_ext}{original_ext}"
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                return f"images/products/{filename}"
        except Exception as e:
            # If conversion fails, try to save original file
            try:
                file.seek(0)  # Reset file pointer
                # Fallback to original extension
                original_ext = os.path.splitext(name)[1]
                filename = f"product_{product_id}_{name_without_ext}{original_ext}"
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                return f"images/products/{filename}"
            except Exception:
                return None
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
