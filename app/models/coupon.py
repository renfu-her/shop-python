from datetime import datetime
from app.utils.db import get_db_connection
from app.utils.helpers import calculate_discount

class Coupon:
    def __init__(self, id=None, code=None, discount_type=None, discount_value=None, 
                 min_purchase=None, max_discount=None, valid_from=None, valid_to=None,
                 usage_limit=None, used_count=None, created_by_type=None, created_by_id=None,
                 applicable_to=None, applicable_id=None, created_at=None):
        self.id = id
        self.code = code
        self.discount_type = discount_type
        self.discount_value = discount_value
        self.min_purchase = min_purchase
        self.max_discount = max_discount
        self.valid_from = valid_from
        self.valid_to = valid_to
        self.usage_limit = usage_limit
        self.used_count = used_count
        self.created_by_type = created_by_type
        self.created_by_id = created_by_id
        self.applicable_to = applicable_to
        self.applicable_id = applicable_id
        self.created_at = created_at
    
    @staticmethod
    def create(code, discount_type, discount_value, min_purchase=0, max_discount=None,
               valid_from=None, valid_to=None, usage_limit=None, created_by_type=None,
               created_by_id=None, applicable_to='all', applicable_id=None):
        """Create new coupon"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Check if code already exists
                cursor.execute("SELECT id FROM coupons WHERE code = %s", (code,))
                if cursor.fetchone():
                    return None, "此優惠券代碼已被使用"
                
                # Set default validity if not provided
                if not valid_from:
                    valid_from = datetime.now()
                if not valid_to:
                    valid_to = datetime(2025, 12, 31)  # Default to end of next year
                
                cursor.execute("""
                    INSERT INTO coupons (code, discount_type, discount_value, min_purchase, max_discount,
                                       valid_from, valid_to, usage_limit, created_by_type, created_by_id,
                                       applicable_to, applicable_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (code, discount_type, discount_value, min_purchase, max_discount,
                      valid_from, valid_to, usage_limit, created_by_type, created_by_id,
                      applicable_to, applicable_id))
                
                coupon_id = cursor.lastrowid
                conn.commit()
                
                return Coupon(id=coupon_id, code=code, discount_type=discount_type,
                             discount_value=discount_value, min_purchase=min_purchase,
                             max_discount=max_discount, valid_from=valid_from, valid_to=valid_to,
                             usage_limit=usage_limit, used_count=0, created_by_type=created_by_type,
                             created_by_id=created_by_id, applicable_to=applicable_to,
                             applicable_id=applicable_id), None
        except Exception as e:
            return None, str(e)
        finally:
            conn.close()
    
    @staticmethod
    def get_by_code(code):
        """Get coupon by code"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, code, discount_type, discount_value, min_purchase, max_discount,
                           valid_from, valid_to, usage_limit, used_count, created_by_type,
                           created_by_id, applicable_to, applicable_id, created_at
                    FROM coupons WHERE code = %s
                """, (code,))
                result = cursor.fetchone()
                if result:
                    return Coupon(**result)
                return None
        except Exception as e:
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_by_creator(created_by_type, created_by_id):
        """Get coupons created by specific user/store"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, code, discount_type, discount_value, min_purchase, max_discount,
                           valid_from, valid_to, usage_limit, used_count, created_by_type,
                           created_by_id, applicable_to, applicable_id, created_at
                    FROM coupons 
                    WHERE created_by_type = %s AND created_by_id = %s
                    ORDER BY created_at DESC
                """, (created_by_type, created_by_id))
                results = cursor.fetchall()
                return [Coupon(**result) for result in results]
        except Exception as e:
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_all():
        """Get all coupons"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, code, discount_type, discount_value, min_purchase, max_discount,
                           valid_from, valid_to, usage_limit, used_count, created_by_type,
                           created_by_id, applicable_to, applicable_id, created_at
                    FROM coupons 
                    ORDER BY created_at DESC
                """)
                results = cursor.fetchall()
                return [Coupon(**result) for result in results]
        except Exception as e:
            return []
        finally:
            conn.close()
    
    def is_valid(self, total_amount=0, product_ids=None, store_id=None):
        """Check if coupon is valid for given conditions"""
        now = datetime.now()
        
        # Check validity period
        if self.valid_from and now < self.valid_from:
            return False, "優惠券尚未生效"
        if self.valid_to and now > self.valid_to:
            return False, "優惠券已過期"
        
        # Check usage limit
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False, "優惠券使用次數已達上限"
        
        # Check minimum purchase
        if self.min_purchase and total_amount < self.min_purchase:
            return False, f"訂單金額需滿 ${self.min_purchase:,.0f} 才能使用此優惠券"
        
        # Check applicability
        if self.applicable_to == 'store' and self.applicable_id != store_id:
            return False, "此優惠券不適用於此商店"
        
        if self.applicable_to == 'category' and product_ids:
            # Check if any product belongs to the specified category
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    placeholders = ','.join(['%s'] * len(product_ids))
                    cursor.execute(f"""
                        SELECT COUNT(*) as count FROM products 
                        WHERE id IN ({placeholders}) AND category_id = %s
                    """, product_ids + [self.applicable_id])
                    if cursor.fetchone()['count'] == 0:
                        return False, "此優惠券不適用於此商品分類"
            finally:
                conn.close()
        
        return True, "優惠券有效"
    
    def calculate_discount(self, total_amount):
        """Calculate discount amount for given total"""
        return calculate_discount(total_amount, self.discount_type, self.discount_value, self.max_discount)
    
    def use_coupon(self):
        """Mark coupon as used"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE coupons SET used_count = used_count + 1 WHERE id = %s",
                    (self.id,)
                )
                conn.commit()
                self.used_count += 1
                return True
        except Exception as e:
            return False
        finally:
            conn.close()
    
    def update(self, code=None, discount_type=None, discount_value=None, min_purchase=None,
               max_discount=None, valid_from=None, valid_to=None, usage_limit=None):
        """Update coupon"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                updates = []
                params = []
                
                if code is not None:
                    # Check if new code already exists
                    cursor.execute("SELECT id FROM coupons WHERE code = %s AND id != %s", (code, self.id))
                    if cursor.fetchone():
                        return False, "此優惠券代碼已被使用"
                    updates.append("code = %s")
                    params.append(code)
                    self.code = code
                
                if discount_type is not None:
                    updates.append("discount_type = %s")
                    params.append(discount_type)
                    self.discount_type = discount_type
                
                if discount_value is not None:
                    updates.append("discount_value = %s")
                    params.append(discount_value)
                    self.discount_value = discount_value
                
                if min_purchase is not None:
                    updates.append("min_purchase = %s")
                    params.append(min_purchase)
                    self.min_purchase = min_purchase
                
                if max_discount is not None:
                    updates.append("max_discount = %s")
                    params.append(max_discount)
                    self.max_discount = max_discount
                
                if valid_from is not None:
                    updates.append("valid_from = %s")
                    params.append(valid_from)
                    self.valid_from = valid_from
                
                if valid_to is not None:
                    updates.append("valid_to = %s")
                    params.append(valid_to)
                    self.valid_to = valid_to
                
                if usage_limit is not None:
                    updates.append("usage_limit = %s")
                    params.append(usage_limit)
                    self.usage_limit = usage_limit
                
                if updates:
                    params.append(self.id)
                    cursor.execute(
                        f"UPDATE coupons SET {', '.join(updates)} WHERE id = %s",
                        params
                    )
                    conn.commit()
                return True, None
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()
    
    def delete(self):
        """Delete coupon"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM coupons WHERE id = %s", (self.id,))
                conn.commit()
                return True
        except Exception as e:
            return False
        finally:
            conn.close()
