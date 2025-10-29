"""
重置管理员密码脚本
运行此脚本来重置或创建管理员账户
"""
from app import create_app
from app.utils.db import get_db_connection
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 检查是否存在 admin 用户
            cursor.execute("SELECT id FROM users WHERE username = %s", ('admin',))
            existing_user = cursor.fetchone()
            
            password_hash = generate_password_hash('admin')
            
            if existing_user:
                # 更新现有用户的密码
                cursor.execute(
                    "UPDATE users SET password_hash = %s WHERE username = %s",
                    (password_hash, 'admin')
                )
                print("✓ 管理员密码已更新")
                print("  用户名: admin")
                print("  密码: admin")
            else:
                # 创建新用户
                cursor.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                    ('admin', password_hash, 'admin')
                )
                print("✓ 管理员账户已创建")
                print("  用户名: admin")
                print("  密码: admin")
            
            conn.commit()
    except Exception as e:
        print(f"✗ 错误: {e}")
    finally:
        conn.close()

