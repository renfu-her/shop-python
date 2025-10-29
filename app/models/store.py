from app.utils.db import get_db_connection

class Store:
    def __init__(self, id=None, member_id=None, store_name=None, description=None, status=None, created_at=None):
        self.id = id
        self.member_id = member_id
        self.store_name = store_name
        self.description = description
        self.status = status
        self.created_at = created_at
    
    @staticmethod
    def create(member_id, store_name, description=None):
        """Create new store"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO stores (member_id, store_name, description) VALUES (%s, %s, %s)",
                    (member_id, store_name, description)
                )
                store_id = cursor.lastrowid
                conn.commit()
                return Store(id=store_id, member_id=member_id, store_name=store_name, description=description, status='pending'), None
        except Exception as e:
            return None, str(e)
        finally:
            conn.close()
    
    @staticmethod
    def get_by_member(member_id):
        """Get all stores owned by member"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, member_id, store_name, description, status, created_at FROM stores WHERE member_id = %s ORDER BY created_at DESC",
                    (member_id,)
                )
                results = cursor.fetchall()
                return [Store(**result) for result in results]
        except Exception as e:
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_by_id(store_id):
        """Get store by ID"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, member_id, store_name, description, status, created_at FROM stores WHERE id = %s",
                    (store_id,)
                )
                result = cursor.fetchone()
                if result:
                    return Store(**result)
                return None
        except Exception as e:
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_all_active():
        """Get all active stores"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT s.id, s.member_id, s.store_name, s.description, s.status, s.created_at, m.name as owner_name FROM stores s JOIN members m ON s.member_id = m.id WHERE s.status = 'active' ORDER BY s.created_at DESC"
                )
                results = cursor.fetchall()
                return results
        except Exception as e:
            return []
        finally:
            conn.close()
    
    def update(self, store_name=None, description=None, status=None):
        """Update store information"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                updates = []
                params = []
                
                if store_name is not None:
                    updates.append("store_name = %s")
                    params.append(store_name)
                    self.store_name = store_name
                
                if description is not None:
                    updates.append("description = %s")
                    params.append(description)
                    self.description = description
                
                if status is not None:
                    updates.append("status = %s")
                    params.append(status)
                    self.status = status
                
                if updates:
                    params.append(self.id)
                    cursor.execute(
                        f"UPDATE stores SET {', '.join(updates)} WHERE id = %s",
                        params
                    )
                    conn.commit()
                return True
        except Exception as e:
            return False
        finally:
            conn.close()
    
    def get_stats(self):
        """Get store statistics"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Get product count
                cursor.execute("SELECT COUNT(*) as product_count FROM products WHERE store_id = %s", (self.id,))
                product_count = cursor.fetchone()['product_count']
                
                # Get order count
                cursor.execute("""
                    SELECT COUNT(DISTINCT o.id) as order_count 
                    FROM orders o 
                    JOIN order_items oi ON o.id = oi.order_id 
                    JOIN products p ON oi.product_id = p.id 
                    WHERE p.store_id = %s
                """, (self.id,))
                order_count = cursor.fetchone()['order_count']
                
                # Get total sales
                cursor.execute("""
                    SELECT COALESCE(SUM(oi.subtotal), 0) as total_sales 
                    FROM orders o 
                    JOIN order_items oi ON o.id = oi.order_id 
                    JOIN products p ON oi.product_id = p.id 
                    WHERE p.store_id = %s AND o.status != 'cancelled'
                """, (self.id,))
                total_sales = cursor.fetchone()['total_sales']
                
                return {
                    'product_count': product_count,
                    'order_count': order_count,
                    'total_sales': total_sales
                }
        except Exception as e:
            return {'product_count': 0, 'order_count': 0, 'total_sales': 0}
        finally:
            conn.close()
