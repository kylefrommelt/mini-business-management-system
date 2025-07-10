"""
Main Routes - Frontend interface and general endpoints
"""
from flask import Blueprint, render_template, jsonify
from backend.app.models import Customer, Product, Order

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')

@main_bp.route('/customers')
def customers_page():
    """Customer management page."""
    return render_template('customers.html')

@main_bp.route('/products')
def products_page():
    """Product management page."""
    return render_template('products.html')

@main_bp.route('/orders')
def orders_page():
    """Order management page."""
    return render_template('orders.html')

@main_bp.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Mini Business Management System'
    })

@main_bp.route('/api/status')
def api_status():
    """API status endpoint with basic statistics."""
    try:
        customer_count = Customer.query.count()
        product_count = Product.query.count()
        order_count = Order.query.count()
        
        return jsonify({
            'status': 'operational',
            'database': 'connected',
            'statistics': {
                'customers': customer_count,
                'products': product_count,
                'orders': order_count
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'database': 'disconnected',
            'error': str(e)
        }), 500 