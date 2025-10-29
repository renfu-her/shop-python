from app.utils.db import get_db_connection
from app.utils.helpers import save_product_image

class Product:
    def __init__(self, id=None, store_id=None, category_id=None, name=None, description=None, 
                 price=None, discount_price=None, stock=None, image_url=None, status=None, created_at=None):
        self.id = id
        self.store_id = store_id
        self.category_id = category_id
        self.name = name
        self.description = description
        self.price = price
        self.discount_price = discount_price
        self.stock = stock
        self.image_url = image_url
        self.status = status
        self.created_at = created_at
    
    @staticmethod
    def create(store_id, category_id, name, description, price, discount_price=None, stock=0, image_file=None):
        """Create new product"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Save image if provided
                image_url = None
                if image_file:
                    # We'll get the product ID after insertion, so we'll save image later
                    pass
                
                cursor.execute(
                    "INSERT INTO products (store_id, category_id, name, description, price, discount_price, stock) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (store_id, category_id, name, description, price, discount_price, stock)
                )
                product_id = cursor.lastrowid
                
                # Save image with product ID
                if image_file:
                    image_url = save_product_image(image_file, product_id)
                    if image_url:
                        cursor.execute(
                            "UPDATE products SET image_url = %s WHERE id = %s",
                            (image_url, product_id)
                        )
                
                conn.commit()
                return Product(id=product_id, store_id=store_id, category_id=category_id, 
                             name=name, description=description, price=price, discount_price=discount_price, 
                             stock=stock, image_url=image_url, status='active'), None
        except Exception as e:
            return None, str(e)
        finally:
            conn.close()
    
    @staticmethod
    def get_by_id(product_id):
        """Get product by ID"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT p.id, p.store_id, p.category_id, p.name, p.description, p.price, 
                           p.discount_price, p.stock, p.image_url, p.status, p.created_at,
                           s.store_name, c.name as category_name
                    FROM products p
                    JOIN stores s ON p.store_id = s.id
                    JOIN categories c ON p.category_id = c.id
                    WHERE p.id = %s
                """, (product_id,))
                result = cursor.fetchone()
                if result:
                    return Product(**{k: v for k, v in result.items() if k in ['id', 'store_id', 'category_id', 'name', 'description', 'price', 'discount_price', 'stock', 'image_url', 'status', 'created_at']})
                return None
        except Exception as e:
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_by_store(store_id, status='active'):
        """Get products by store"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT p.id, p.store_id, p.category_id, p.name, p.description, p.price, 
                           p.discount_price, p.stock, p.image_url, p.status, p.created_at,
                           c.name as category_name
                    FROM products p
                    JOIN categories c ON p.category_id = c.id
                    WHERE p.store_id = %s AND p.status = %s
                    ORDER BY p.created_at DESC
                """, (store_id, status))
                results = cursor.fetchall()
                return [Product(**{k: v for k, v in result.items() if k in ['id', 'store_id', 'category_id', 'name', 'description', 'price', 'discount_price', 'stock', 'image_url', 'status', 'created_at']}) for result in results]
        except Exception as e:
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_all_active(category_id=None, search=None, page=1, per_page=12):
        """Get all active products with pagination"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                where_conditions = ["p.status = 'active'", "s.status = 'active'"]
                params = []
                
                if category_id:
                    where_conditions.append("p.category_id = %s")
                    params.append(category_id)
                
                if search:
                    where_conditions.append("(p.name LIKE %s OR p.description LIKE %s)")
                    search_term = f"%{search}%"
                    params.extend([search_term, search_term])
                
                where_clause = " AND ".join(where_conditions)
                
                # Get total count
                count_sql = f"""
                    SELECT COUNT(*) as total
                    FROM products p
                    JOIN stores s ON p.store_id = s.id
                    WHERE {where_clause}
                """
                cursor.execute(count_sql, params)
                total = cursor.fetchone()['total']
                
                # Get products with pagination
                offset = (page - 1) * per_page
                sql = f"""
                    SELECT p.id, p.store_id, p.category_id, p.name, p.description, p.price, 
                           p.discount_price, p.stock, p.image_url, p.status, p.created_at,
                           s.store_name, c.name as category_name
                    FROM products p
                    JOIN stores s ON p.store_id = s.id
                    JOIN categories c ON p.category_id = c.id
                    WHERE {where_clause}
                    ORDER BY p.created_at DESC
                    LIMIT %s OFFSET %s
                """
                cursor.execute(sql, params + [per_page, offset])
                results = cursor.fetchall()
                
                products = [Product(**{k: v for k, v in result.items() if k in ['id', 'store_id', 'category_id', 'name', 'description', 'price', 'discount_price', 'stock', 'image_url', 'status', 'created_at']}) for result in results]
                
                return products, total
        except Exception as e:
            return [], 0
        finally:
            conn.close()
    
    def update(self, name=None, description=None, price=None, discount_price=None, stock=None, category_id=None, status=None, image_file=None):
        """Update product"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                updates = []
                params = []
                
                if name is not None:
                    updates.append("name = %s")
                    params.append(name)
                    self.name = name
                
                if description is not None:
                    updates.append("description = %s")
                    params.append(description)
                    self.description = description
                
                if price is not None:
                    updates.append("price = %s")
                    params.append(price)
                    self.price = price
                
                if discount_price is not None:
                    updates.append("discount_price = %s")
                    params.append(discount_price)
                    self.discount_price = discount_price
                
                if stock is not None:
                    updates.append("stock = %s")
                    params.append(stock)
                    self.stock = stock
                
                if category_id is not None:
                    updates.append("category_id = %s")
                    params.append(category_id)
                    self.category_id = category_id
                
                if status is not None:
                    updates.append("status = %s")
                    params.append(status)
                    self.status = status
                
                # Handle image upload
                if image_file:
                    image_url = save_product_image(image_file, self.id)
                    if image_url:
                        updates.append("image_url = %s")
                        params.append(image_url)
                        self.image_url = image_url
                
                if updates:
                    params.append(self.id)
                    cursor.execute(
                        f"UPDATE products SET {', '.join(updates)} WHERE id = %s",
                        params
                    )
                    conn.commit()
                return True
        except Exception as e:
            return False
        finally:
            conn.close()
    
    def delete(self):
        """Delete product"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM products WHERE id = %s", (self.id,))
                conn.commit()
                return True
        except Exception as e:
            return False
        finally:
            conn.close()
    
    def get_effective_price(self):
        """Get effective price (discount_price if available, otherwise price)"""
        return self.discount_price if self.discount_price else self.price
    
    def is_in_stock(self):
        """Check if product is in stock"""
        return self.stock > 0

    # New: Homepage data helpers
    @staticmethod
    def get_top_new(limit=8):
        """Get newest active products across active stores (for 熱門商品)."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT p.id, p.store_id, p.category_id, p.name, p.description, p.price,
                           p.discount_price, p.stock, p.image_url, p.status, p.created_at,
                           s.store_name, c.name as category_name
                    FROM products p
                    JOIN stores s ON p.store_id = s.id
                    JOIN categories c ON p.category_id = c.id
                    WHERE p.status = 'active' AND s.status = 'active'
                    ORDER BY p.created_at DESC
                    LIMIT %s
                    """,
                    (limit,)
                )
                results = cursor.fetchall()
                return [Product(**{k: v for k, v in result.items() if k in ['id', 'store_id', 'category_id', 'name', 'description', 'price', 'discount_price', 'stock', 'image_url', 'status', 'created_at']}) for result in results]
        except Exception:
            return []
        finally:
            conn.close()

    @staticmethod
    def get_top_best_sellers(limit=8):
        """Get best-selling products by total quantity sold (for 熱銷商品)."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT p.id, p.store_id, p.category_id, p.name, p.description, p.price,
                           p.discount_price, p.stock, p.image_url, p.status, p.created_at,
                           s.store_name, c.name as category_name,
                           SUM(oi.quantity) AS sold_qty
                    FROM order_items oi
                    JOIN products p ON oi.product_id = p.id
                    JOIN stores s ON p.store_id = s.id
                    JOIN categories c ON p.category_id = c.id
                    WHERE p.status = 'active' AND s.status = 'active'
                    GROUP BY p.id
                    ORDER BY sold_qty DESC
                    LIMIT %s
                    """,
                    (limit,)
                )
                results = cursor.fetchall()
                return [Product(**{k: v for k, v in result.items() if k in ['id', 'store_id', 'category_id', 'name', 'description', 'price', 'discount_price', 'stock', 'image_url', 'status', 'created_at']}) for result in results]
        except Exception:
            return []
        finally:
            conn.close()