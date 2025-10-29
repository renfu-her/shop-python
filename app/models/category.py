from app.utils.db import get_db_connection

class Category:
    def __init__(self, id=None, name=None, description=None, created_at=None):
        self.id = id
        self.name = name
        self.description = description
        self.created_at = created_at
    
    @staticmethod
    def get_all():
        """Get all categories"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, name, description, created_at FROM categories ORDER BY name"
                )
                results = cursor.fetchall()
                return [Category(**result) for result in results]
        except Exception as e:
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_with_products():
        """Get only categories that have active products"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT c.id, c.name, c.description, c.created_at
                    FROM categories c
                    INNER JOIN products p ON c.id = p.category_id
                    INNER JOIN stores s ON p.store_id = s.id
                    WHERE p.status = 'active' AND s.status = 'active'
                    ORDER BY c.name
                """)
                results = cursor.fetchall()
                return [Category(**result) for result in results]
        except Exception as e:
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_by_id(category_id):
        """Get category by ID"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, name, description, created_at FROM categories WHERE id = %s",
                    (category_id,)
                )
                result = cursor.fetchone()
                if result:
                    return Category(**result)
                return None
        except Exception as e:
            return None
        finally:
            conn.close()
    
    @staticmethod
    def create(name, description=None):
        """Create new category"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO categories (name, description) VALUES (%s, %s)",
                    (name, description)
                )
                category_id = cursor.lastrowid
                conn.commit()
                return Category(id=category_id, name=name, description=description), None
        except Exception as e:
            return None, str(e)
        finally:
            conn.close()
    
    def update(self, name=None, description=None):
        """Update category"""
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
                
                if updates:
                    params.append(self.id)
                    cursor.execute(
                        f"UPDATE categories SET {', '.join(updates)} WHERE id = %s",
                        params
                    )
                    conn.commit()
                return True
        except Exception as e:
            return False
        finally:
            conn.close()
    
    def delete(self):
        """Delete category"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Check if category has products
                cursor.execute("SELECT COUNT(*) as count FROM products WHERE category_id = %s", (self.id,))
                if cursor.fetchone()['count'] > 0:
                    return False, "此分類下還有商品，無法刪除"
                
                cursor.execute("DELETE FROM categories WHERE id = %s", (self.id,))
                conn.commit()
                return True, None
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()
