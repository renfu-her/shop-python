import pymysql
from flask import current_app

def get_db_connection():
    """Get database connection"""
    return pymysql.connect(
        host=current_app.config['MYSQL_HOST'],
        user=current_app.config['MYSQL_USER'],
        password=current_app.config['MYSQL_PASSWORD'],
        database=current_app.config['MYSQL_DB'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def init_db(app):
    """Initialize database tables"""
    with app.app_context():
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Create tables
                create_tables_sql = """
                CREATE TABLE IF NOT EXISTS members (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    phone VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role ENUM('admin', 'manager') DEFAULT 'admin',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS stores (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    member_id INT NOT NULL,
                    store_name VARCHAR(255) NOT NULL,
                    description TEXT,
                    status ENUM('active', 'inactive', 'pending') DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
                );
                
                CREATE TABLE IF NOT EXISTS categories (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS products (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    store_id INT NOT NULL,
                    category_id INT NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    price DECIMAL(10,2) NOT NULL,
                    discount_price DECIMAL(10,2),
                    stock INT DEFAULT 0,
                    image_url VARCHAR(500),
                    status ENUM('active', 'inactive') DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE,
                    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
                );
                
                CREATE TABLE IF NOT EXISTS coupons (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    code VARCHAR(50) UNIQUE NOT NULL,
                    discount_type ENUM('percentage', 'fixed') NOT NULL,
                    discount_value DECIMAL(10,2) NOT NULL,
                    min_purchase DECIMAL(10,2) DEFAULT 0,
                    max_discount DECIMAL(10,2),
                    valid_from TIMESTAMP NOT NULL,
                    valid_to TIMESTAMP NOT NULL,
                    usage_limit INT DEFAULT NULL,
                    used_count INT DEFAULT 0,
                    created_by_type ENUM('admin', 'store') NOT NULL,
                    created_by_id INT NOT NULL,
                    applicable_to ENUM('all', 'store', 'category') DEFAULT 'all',
                    applicable_id INT DEFAULT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS orders (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    member_id INT NOT NULL,
                    order_number VARCHAR(50) UNIQUE NOT NULL,
                    total_amount DECIMAL(10,2) NOT NULL,
                    discount_amount DECIMAL(10,2) DEFAULT 0,
                    final_amount DECIMAL(10,2) NOT NULL,
                    coupon_id INT DEFAULT NULL,
                    status ENUM('pending', 'confirmed', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE,
                    FOREIGN KEY (coupon_id) REFERENCES coupons(id) ON DELETE SET NULL
                );
                
                CREATE TABLE IF NOT EXISTS order_items (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    order_id INT NOT NULL,
                    product_id INT NOT NULL,
                    quantity INT NOT NULL,
                    price DECIMAL(10,2) NOT NULL,
                    subtotal DECIMAL(10,2) NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
                );
                
                CREATE TABLE IF NOT EXISTS cart (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    member_id INT NOT NULL,
                    product_id INT NOT NULL,
                    quantity INT NOT NULL DEFAULT 1,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_cart_item (member_id, product_id)
                );
                
                # Insert default categories
                INSERT IGNORE INTO categories (name, description) VALUES
                ('3C', '電腦、手機、平板等電子產品'),
                ('周邊', '電腦周邊設備'),
                ('筆電', '筆記型電腦'),
                ('通訊', '手機、通訊設備'),
                ('數位', '數位相機、攝影器材'),
                ('家電', '家用電器'),
                ('日用', '日常生活用品'),
                ('母嬰', '母嬰用品'),
                ('食品', '食品飲料'),
                ('生活', '生活用品'),
                ('居家', '居家裝飾'),
                ('休閒', '休閒娛樂'),
                ('保健', '保健用品'),
                ('美妝', '美妝保養'),
                ('時尚', '時尚服飾'),
                ('書店', '書籍文具');
                
                # Insert default admin user (password: admin123)
                INSERT IGNORE INTO users (username, password_hash, role) VALUES
                ('admin', 'scrypt:32768:8:1$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4Qz8z8z8z8', 'admin');
                """
                
                # Execute each CREATE TABLE statement separately
                statements = create_tables_sql.split(';')
                for statement in statements:
                    statement = statement.strip()
                    if statement:
                        cursor.execute(statement)
                conn.commit()
                
        except Exception as e:
            print(f"Database initialization error: {e}")
        finally:
            conn.close()
