from flask import Flask, render_template
from config import Config
from app.utils.db import init_db
import os
import logging
from logging.handlers import RotatingFileHandler
from app.extensions import db

def create_app(config_class=Config):
    # Get the absolute path to the app directory
    app_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(app_dir, 'views')
    static_dir = os.path.join(app_dir, 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir, 
                static_folder=static_dir, 
                static_url_path='/static')
    app.config.from_object(config_class)
    
    # Setup logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/shop.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Shop startup')
    
    # Enable debug toolbar-like features in development
    if app.debug:
        app.logger.setLevel(logging.DEBUG)
        app.logger.debug('Debug mode enabled')
    
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
    app.register_blueprint(product_bp)
    app.register_blueprint(cart_bp, url_prefix='/cart')
    app.register_blueprint(order_bp, url_prefix='/order')
    app.register_blueprint(coupon_bp, url_prefix='/coupon')
    app.register_blueprint(admin_bp, url_prefix='/backend')
    
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
