"""
Flask Application Factory
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, 
                static_folder='../../frontend/static',
                template_folder='../../frontend/templates')
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 
        'postgresql://postgres:password@localhost/bizowie_erp'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    # Import models (required for migrations)
    from backend.app import models
    
    # Register blueprints
    from backend.app.routes import customer_routes, product_routes, order_routes, analytics_routes
    from backend.app.routes.main_routes import main_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(customer_routes.bp)
    app.register_blueprint(product_routes.bp)
    app.register_blueprint(order_routes.bp)
    app.register_blueprint(analytics_routes.bp)
    
    return app 