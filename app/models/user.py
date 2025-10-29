from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.db import get_db_connection

class User:
    def __init__(self, id=None, username=None, password_hash=None, role=None, created_at=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.created_at = created_at
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password"""
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def get_by_username(username):
        """Get user by username"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, username, password_hash, role, created_at FROM users WHERE username = %s",
                    (username,)
                )
                result = cursor.fetchone()
                if result:
                    return User(**result)
                return None
        except Exception as e:
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, username, password_hash, role, created_at FROM users WHERE id = %s",
                    (user_id,)
                )
                result = cursor.fetchone()
                if result:
                    return User(**result)
                return None
        except Exception as e:
            return None
        finally:
            conn.close()
    
    @staticmethod
    def create(username, password, role='admin'):
        """Create new admin user"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Check if username already exists
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                if cursor.fetchone():
                    return None, "此使用者名稱已被使用"
                
                # Create new user
                user = User(username=username, role=role)
                user.set_password(password)
                
                cursor.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                    (user.username, user.password_hash, user.role)
                )
                user.id = cursor.lastrowid
                conn.commit()
                return user, None
        except Exception as e:
            return None, str(e)
        finally:
            conn.close()
    
    @staticmethod
    def get_all():
        """Get all users"""
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, username, role, created_at FROM users ORDER BY created_at DESC"
                )
                results = cursor.fetchall()
                return [User(**result) for result in results]
        except Exception as e:
            return []
        finally:
            conn.close()
