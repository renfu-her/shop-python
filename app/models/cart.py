from app.utils.db import get_db_connection

class Cart:
    def __init__(self, id=None, member_id=None, product_id=None, quantity=None, added_at=None):
        self.id = id
        self.member_id = member_id
        self.product_id = product_id
        self.quantity = quantity
        self.added_at = added_at
    
    @staticmethod
    def add_item(member_id, product_id, quantity=1):
        """Add item to cart"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Check if item already exists in cart
                cursor.execute(
                    "SELECT id, quantity FROM cart WHERE member_id = %s AND product_id = %s",
                    (member_id, product_id)
                )
                existing = cursor.fetchone()
                
                if existing:
                    # Update quantity
                    new_quantity = existing['quantity'] + quantity
                    cursor.execute(
                        "UPDATE cart SET quantity = %s WHERE id = %s",
                        (new_quantity, existing['id'])
                    )
                else:
                    # Add new item
                    cursor.execute(
                        "INSERT INTO cart (member_id, product_id, quantity) VALUES (%s, %s, %s)",
                        (member_id, product_id, quantity)
                    )
                
                conn.commit()
                return True, None
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()
    
    @staticmethod
    def get_by_member(member_id):
        """Get cart items for member"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT c.id, c.member_id, c.product_id, c.quantity, c.added_at,
                           p.name as product_name, p.price, p.discount_price, p.image_url,
                           p.stock, s.store_name, s.id as store_id
                    FROM cart c
                    JOIN products p ON c.product_id = p.id
                    JOIN stores s ON p.store_id = s.id
                    WHERE c.member_id = %s AND p.status = 'active' AND s.status = 'active'
                    ORDER BY c.added_at DESC
                """, (member_id,))
                
                results = cursor.fetchall()
                cart_items = []
                
                for result in results:
                    # Calculate effective price
                    effective_price = result['discount_price'] if result['discount_price'] else result['price']
                    subtotal = effective_price * result['quantity']
                    
                    cart_items.append({
                        'id': result['id'],
                        'product_id': result['product_id'],
                        'product_name': result['product_name'],
                        'price': effective_price,
                        'original_price': result['price'],
                        'discount_price': result['discount_price'],
                        'quantity': result['quantity'],
                        'subtotal': subtotal,
                        'image_url': result['image_url'],
                        'stock': result['stock'],
                        'store_name': result['store_name'],
                        'store_id': result['store_id'],
                        'added_at': result['added_at']
                    })
                
                return cart_items
        except Exception as e:
            return []
        finally:
            conn.close()
    
    @staticmethod
    def update_quantity(member_id, product_id, quantity):
        """Update item quantity in cart"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                if quantity <= 0:
                    # Remove item if quantity is 0 or negative
                    cursor.execute(
                        "DELETE FROM cart WHERE member_id = %s AND product_id = %s",
                        (member_id, product_id)
                    )
                else:
                    # Update quantity
                    cursor.execute(
                        "UPDATE cart SET quantity = %s WHERE member_id = %s AND product_id = %s",
                        (quantity, member_id, product_id)
                    )
                
                conn.commit()
                return True, None
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()
    
    @staticmethod
    def remove_item(member_id, product_id):
        """Remove item from cart"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM cart WHERE member_id = %s AND product_id = %s",
                    (member_id, product_id)
                )
                conn.commit()
                return True, None
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()
    
    @staticmethod
    def clear_cart(member_id):
        """Clear all items from cart"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM cart WHERE member_id = %s", (member_id,))
                conn.commit()
                return True, None
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()
    
    @staticmethod
    def get_cart_summary(member_id):
        """Get cart summary (total items, total amount)"""
        cart_items = Cart.get_by_member(member_id)
        
        total_items = sum(item['quantity'] for item in cart_items)
        total_amount = sum(item['subtotal'] for item in cart_items)
        
        return {
            'total_items': total_items,
            'total_amount': total_amount,
            'items': cart_items
        }
