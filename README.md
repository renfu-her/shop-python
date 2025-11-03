# DEMO Mall (E-commerce Platform)

DEMO Mall is a Flask-based e-commerce platform with a multi-store model, featuring cart, coupons, and order management. The project uses server-side templates and modern UI components for a clean shopping experience.

## Features

### 🛍️ Shopping
- Product browsing with category filters and search
- Cart: add, update quantity, remove
- Checkout with coupon support
- Order tracking and status updates

### 👥 Member System
- Member registration and login
- Profile management
- My Stores: members can create multiple stores
- Order history

### 🏪 Store Management
- Store creation and review flow
- Product CRUD
- Store order management
- Store-specific coupons

### 👨‍💼 Admin Console
- Admin authentication
- Store review (enable/disable)
- User management
- Global coupons
- Order monitoring

### 🎫 Coupon System
- Percentage and fixed amount discounts
- Constraints: min spend, max discount, usage limits
- Scope: global, store-specific, category-specific
- Validity period control (start/end time)

## Tech Stack

### Backend
- Flask 2.3.3
- MySQL
- ORM: Flask-SQLAlchemy (SQLAlchemy 2.x). Legacy PyMySQL access is kept for backward compatibility during migration
- Forms: WTForms
- Auth: Werkzeug Security

### Frontend
- Bootstrap 5.3.0
- Font Awesome 6.x
- Vanilla JS + Bootstrap JS

### Database Schema (tables)
- members, users, stores, categories, products, coupons, orders, order_items, cart

## Getting Started

### 1) Prerequisites
- Python 3.8+
- MySQL 5.7+
- Git

### 2) Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd shop

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Prepare the database
# Ensure MySQL is running, then create database
mysql -u root -p
CREATE DATABASE `shop-data`;

# 6. Environment variables (optional)
echo "SECRET_KEY=your-secret-key-here" > .env

# 7. Run the app
python run.py
```

### 3) Configuration
- Host: `localhost`
- User: `root`
- Password: empty by default (change in `config.py`)
- Database: `shop-data`

The ORM connection string is configured via `SQLALCHEMY_DATABASE_URI` in `config.py`. You can also set `DATABASE_URL` to override it.

### 4) Default Accounts
- Admin: username `admin`, password `admin`
- Member: register via UI

## Usage

### Member Flow
1. Register at `/member/register`
2. Create a store from “My Stores” after login
3. Manage products in your store backend
4. Browse and purchase products

### Admin Flow
<<<<<<< HEAD
1. Login at `/backend/login`
=======
1. Login at `/admin/login`
>>>>>>> 81d1a7905f3154c80b7086052a7b5e11d33a80b3
2. Review stores (enable/disable)
3. Manage site-wide coupons
4. Monitor orders

### Store Operations
1. Add products (name, price, stock, image)
2. Process orders and update statuses
3. Create store-specific coupons
4. Review sales metrics

## Project Structure

```
shop/
├── app/
│   ├── __init__.py                # Flask app factory
│   ├── extensions.py              # SQLAlchemy instance
│   ├── models/
│   │   ├── orm_models.py          # SQLAlchemy ORM models (Product/Store/Category/OrderItem)
│   │   ├── product.py             # Product service layer (compat methods)
│   │   ├── member.py
│   │   ├── user.py
│   │   ├── store.py
│   │   ├── category.py
│   │   ├── coupon.py
│   │   ├── order.py
│   │   └── cart.py
│   ├── controllers/
│   │   ├── member_controller.py
│   │   ├── admin_controller.py
│   │   ├── store_controller.py
│   │   ├── product_controller.py
│   │   ├── cart_controller.py
│   │   ├── order_controller.py
│   │   └── coupon_controller.py
│   ├── utils/
│   │   ├── db.py                  # Legacy MySQL init (still used for some areas)
│   │   ├── auth.py
│   │   └── helpers.py
│   ├── views/                     # Jinja templates
│   │   ├── layout.html
│   │   ├── errors/                # 404 / 500 pages
│   │   ├── member/
│   │   ├── admin/
│   │   ├── store/
│   │   ├── shop/
│   │   ├── cart/
│   │   └── order/
│   └── static/
│       ├── css/style.css
│       ├── js/main.js
│       └── images/
├── config.py
├── requirements.txt
├── run.py
└── README.md
```

## Development Notes

- Error handling: custom 404 and 500 pages are registered in `app/__init__.py` and located at `app/views/errors/`
- Homepage highlights: “Popular” and “Best Sellers” sections each show top 8 items in random order
- ORM migration: key product queries now use SQLAlchemy; legacy raw SQL remains in some modules and can be migrated progressively
- Styling: custom theme in `app/static/css/style.css` with gradient navbar/hero and accent colors

## Security & Operations

1. Change default passwords and `SECRET_KEY` in production
2. Ensure `app/static/images/products/` exists and is writable for uploads
3. Backup MySQL regularly
4. Consider caching when you have many products (homepage currently loads all matching products)

## License

This project is for learning and demo purposes only. Not intended for commercial use.

## Contact

For questions or suggestions, please open an issue or contact the maintainers.
