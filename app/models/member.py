from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.db import get_db_connection

class Member:
    def __init__(self, id=None, email=None, password_hash=None, name=None, phone=None, created_at=None):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.name = name
        self.phone = phone
        self.created_at = created_at
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password"""
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def create(email, password, name, phone=None):
        """Create new member"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Check if email already exists
                cursor.execute("SELECT id FROM members WHERE email = %s", (email,))
                if cursor.fetchone():
                    return None, "此電子郵件已被使用"
                
                # Create new member
                member = Member(email=email, name=name, phone=phone)
                member.set_password(password)
                
                cursor.execute(
                    "INSERT INTO members (email, password_hash, name, phone) VALUES (%s, %s, %s, %s)",
                    (member.email, member.password_hash, member.name, member.phone)
                )
                member.id = cursor.lastrowid
                conn.commit()
                return member, None
        except Exception as e:
            return None, str(e)
        finally:
            conn.close()
    
    @staticmethod
    def get_by_email(email):
        """Get member by email"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, email, password_hash, name, phone, created_at FROM members WHERE email = %s",
                    (email,)
                )
                result = cursor.fetchone()
                if result:
                    return Member(**result)
                return None
        except Exception as e:
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_by_id(member_id):
        """Get member by ID"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, email, password_hash, name, phone, created_at FROM members WHERE id = %s",
                    (member_id,)
                )
                result = cursor.fetchone()
                if result:
                    return Member(**result)
                return None
        except Exception as e:
            return None
        finally:
            conn.close()
    
    def update_profile(self, name=None, phone=None):
        """Update member profile"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                updates = []
                params = []
                
                if name is not None:
                    updates.append("name = %s")
                    params.append(name)
                    self.name = name
                
                if phone is not None:
                    updates.append("phone = %s")
                    params.append(phone)
                    self.phone = phone
                
                if updates:
                    params.append(self.id)
                    cursor.execute(
                        f"UPDATE members SET {', '.join(updates)} WHERE id = %s",
                        params
                    )
                    conn.commit()
                return True
        except Exception as e:
            return False
        finally:
            conn.close()
