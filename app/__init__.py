from flask import Flask, render_template
from config import Config
from app.utils.db import init_db
import os
from app.extensions import db

def create_app():
    # Get the absolute path to the app directory
    app_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(app_dir, 'views')
    static_dir = os.path.join(app_dir, 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir, 
                static_folder=static_dir, 
                static_url_path='/static')
    app.config.from_object(Config)
    
    # Initialize databases
    init_db(app)  # existing PyMySQL usage (kept for backward compatibility)
    db.init_app(app)  # SQLAlchemy ORM
    
    # Register blueprints
    from app.controllers.member_controller import member_bp
    from app.controllers.store_controller import store_bp
    from app.controllers.product_controller import product_bp
    from app.controllers.cart_controller import cart_bp
    from app.controllers.order_controller import order_bp
    from app.controllers.coupon_controller import coupon_bp
    from app.controllers.admin_controller import admin_bp
    
    app.register_blueprint(member_bp, url_prefix='/member')
    app.register_blueprint(store_bp, url_prefix='/store')
    app.register_blueprint(product_bp, url_prefix='/shop')
    app.register_blueprint(cart_bp, url_prefix='/cart')
    app.register_blueprint(order_bp, url_prefix='/order')
    app.register_blueprint(coupon_bp, url_prefix='/coupon')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Root route
    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('product.index'))
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500
    
    return app
