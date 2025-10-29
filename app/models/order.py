from datetime import datetime
from app.utils.db import get_db_connection
from app.utils.helpers import generate_order_number

class Order:
    def __init__(self, id=None, member_id=None, order_number=None, total_amount=None,
                 discount_amount=None, final_amount=None, coupon_id=None, status=None, created_at=None):
        self.id = id
        self.member_id = member_id
        self.order_number = order_number
        self.total_amount = total_amount
        self.discount_amount = discount_amount
        self.final_amount = final_amount
        self.coupon_id = coupon_id
        self.status = status
        self.created_at = created_at
    
    @staticmethod
    def create(member_id, cart_items, coupon_code=None):
        """Create new order from cart items"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Calculate total amount
                total_amount = sum(item['subtotal'] for item in cart_items)
                
                # Apply coupon if provided
                discount_amount = 0
                coupon_id = None
                if coupon_code:
                    from app.models.coupon import Coupon
                    coupon = Coupon.get_by_code(coupon_code)
                    if coupon:
                        product_ids = [item['product_id'] for item in cart_items]
                        store_id = cart_items[0]['store_id'] if cart_items else None
                        
                        is_valid, message = coupon.is_valid(total_amount, product_ids, store_id)
                        if is_valid:
                            discount_amount = coupon.calculate_discount(total_amount)
                            coupon_id = coupon.id
                            coupon.use_coupon()
                
                final_amount = total_amount - discount_amount
                order_number = generate_order_number()
                
                # Create order
                cursor.execute("""
                    INSERT INTO orders (member_id, order_number, total_amount, discount_amount, 
                                      final_amount, coupon_id, status)
                    VALUES (%s, %s, %s, %s, %s, %s, 'pending')
                """, (member_id, order_number, total_amount, discount_amount, final_amount, coupon_id))
                
                order_id = cursor.lastrowid
                
                # Create order items
                for item in cart_items:
                    cursor.execute("""
                        INSERT INTO order_items (order_id, product_id, quantity, price, subtotal)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (order_id, item['product_id'], item['quantity'], item['price'], item['subtotal']))
                
                # Clear cart
                cursor.execute("DELETE FROM cart WHERE member_id = %s", (member_id,))
                
                conn.commit()
                
                return Order(id=order_id, member_id=member_id, order_number=order_number,
                           total_amount=total_amount, discount_amount=discount_amount,
                           final_amount=final_amount, coupon_id=coupon_id, status='pending'), None
        except Exception as e:
            return None, str(e)
        finally:
            conn.close()
    
    @staticmethod
    def get_by_member(member_id, page=1, per_page=10):
        """Get orders by member with pagination"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Get total count
                cursor.execute("SELECT COUNT(*) as total FROM orders WHERE member_id = %s", (member_id,))
                total = cursor.fetchone()['total']
                
                # Get orders with pagination
                offset = (page - 1) * per_page
                cursor.execute("""
                    SELECT id, member_id, order_number, total_amount, discount_amount, 
                           final_amount, coupon_id, status, created_at
                    FROM orders 
                    WHERE member_id = %s 
                    ORDER BY created_at DESC 
                    LIMIT %s OFFSET %s
                """, (member_id, per_page, offset))
                
                results = cursor.fetchall()
                orders = [Order(**result) for result in results]
                
                return orders, total
        except Exception as e:
            return [], 0
        finally:
            conn.close()
    
    @staticmethod
    def get_by_store(store_id, page=1, per_page=10):
        """Get orders for a specific store"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Get total count
                cursor.execute("""
                    SELECT COUNT(DISTINCT o.id) as total
                    FROM orders o
                    JOIN order_items oi ON o.id = oi.order_id
                    JOIN products p ON oi.product_id = p.id
                    WHERE p.store_id = %s
                """, (store_id,))
                total = cursor.fetchone()['total']
                
                # Get orders with pagination
                offset = (page - 1) * per_page
                cursor.execute("""
                    SELECT DISTINCT o.id, o.member_id, o.order_number, o.total_amount, o.discount_amount, 
                           o.final_amount, o.coupon_id, o.status, o.created_at
                    FROM orders o
                    JOIN order_items oi ON o.id = oi.order_id
                    JOIN products p ON oi.product_id = p.id
                    WHERE p.store_id = %s
                    ORDER BY o.created_at DESC 
                    LIMIT %s OFFSET %s
                """, (store_id, per_page, offset))
                
                results = cursor.fetchall()
                orders = [Order(**result) for result in results]
                
                return orders, total
        except Exception as e:
            return [], 0
        finally:
            conn.close()
    
    @staticmethod
    def get_by_id(order_id):
        """Get order by ID"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, member_id, order_number, total_amount, discount_amount, 
                           final_amount, coupon_id, status, created_at
                    FROM orders WHERE id = %s
                """, (order_id,))
                result = cursor.fetchone()
                if result:
                    return Order(**result)
                return None
        except Exception as e:
            return None
        finally:
            conn.close()
    
    def get_items(self):
        """Get order items"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT oi.id, oi.product_id, oi.quantity, oi.price, oi.subtotal,
                           p.name as product_name, p.image_url, s.store_name
                    FROM order_items oi
                    JOIN products p ON oi.product_id = p.id
                    JOIN stores s ON p.store_id = s.id
                    WHERE oi.order_id = %s
                """, (self.id,))
                return cursor.fetchall()
        except Exception as e:
            return []
        finally:
            conn.close()
    
    def update_status(self, status):
        """Update order status"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE orders SET status = %s WHERE id = %s",
                    (status, self.id)
                )
                conn.commit()
                self.status = status
                return True
        except Exception as e:
            return False
        finally:
            conn.close()
    
    @staticmethod
    def get_all(page=1, per_page=10):
        """Get all orders (admin)"""
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
                
                results = cursor.fetchall()
                orders = [Order(**{k: v for k, v in result.items() if k in ['id', 'member_id', 'order_number', 'total_amount', 'discount_amount', 'final_amount', 'coupon_id', 'status', 'created_at']}) for result in results]
                
                return orders, total
        except Exception as e:
            return [], 0
        finally:
            conn.close()
