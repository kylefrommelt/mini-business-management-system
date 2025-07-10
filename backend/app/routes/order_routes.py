"""
Order Routes - REST API endpoints for order processing workflow
"""
from flask import Blueprint, request, jsonify
from backend.app import db
from backend.app.models import Order, OrderItem, Product, Customer
from sqlalchemy import or_

bp = Blueprint('orders', __name__, url_prefix='/api/orders')

@bp.route('', methods=['GET'])
def get_orders():
    """Get all orders with optional filtering and pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status', '')
        customer_id = request.args.get('customer_id', type=int)
        
        query = Order.query
        
        # Apply status filter
        if status:
            query = query.filter(Order.status == status)
        
        # Apply customer filter
        if customer_id:
            query = query.filter(Order.customer_id == customer_id)
        
        # Order by most recent first
        query = query.order_by(Order.created_at.desc())
        
        # Pagination
        orders = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'orders': [order.to_dict() for order in orders.items],
            'pagination': {
                'page': orders.page,
                'pages': orders.pages,
                'per_page': orders.per_page,
                'total': orders.total
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Get a specific order by ID."""
    try:
        order = Order.query.get_or_404(order_id)
        return jsonify(order.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@bp.route('', methods=['POST'])
def create_order():
    """Create a new order."""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('customer_id'):
            return jsonify({'error': 'customer_id is required'}), 400
        
        if not data.get('items') or not isinstance(data['items'], list):
            return jsonify({'error': 'items array is required'}), 400
        
        # Validate customer exists
        customer = Customer.query.get(data['customer_id'])
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        # Create order
        order = Order(
            customer_id=data['customer_id'],
            shipping_address=data.get('shipping_address'),
            shipping_city=data.get('shipping_city'),
            shipping_state=data.get('shipping_state'),
            shipping_zip=data.get('shipping_zip'),
            shipping_country=data.get('shipping_country', 'USA'),
            shipping_amount=data.get('shipping_amount', 0.00)
        )
        
        # Generate order number
        order.order_number = order.generate_order_number()
        
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        # Create order items
        for item_data in data['items']:
            if not all(key in item_data for key in ['product_id', 'quantity']):
                return jsonify({'error': 'Each item must have product_id and quantity'}), 400
            
            product = Product.query.get(item_data['product_id'])
            if not product:
                return jsonify({'error': f'Product {item_data["product_id"]} not found'}), 404
            
            # Check stock availability
            if product.stock_quantity < item_data['quantity']:
                return jsonify({'error': f'Insufficient stock for product {product.name}'}), 400
            
            # Create order item
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item_data['quantity'],
                unit_price=product.price
            )
            order_item.calculate_line_total()
            
            # Reduce product stock
            product.reduce_stock(item_data['quantity'])
            
            db.session.add(order_item)
        
        # Calculate order totals
        order.calculate_totals()
        
        db.session.commit()
        
        return jsonify(order.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Update order status."""
    try:
        order = Order.query.get_or_404(order_id)
        data = request.get_json()
        
        new_status = data.get('status')
        if not new_status:
            return jsonify({'error': 'status is required'}), 400
        
        if new_status not in Order.VALID_STATUSES:
            return jsonify({'error': f'Invalid status. Valid options: {Order.VALID_STATUSES}'}), 400
        
        if not order.update_status(new_status):
            return jsonify({'error': f'Cannot transition from {order.status} to {new_status}'}), 400
        
        db.session.commit()
        
        return jsonify(order.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:order_id>', methods=['DELETE'])
def cancel_order(order_id):
    """Cancel an order (only if status is Pending)."""
    try:
        order = Order.query.get_or_404(order_id)
        
        if order.status != Order.STATUS_PENDING:
            return jsonify({'error': 'Only pending orders can be cancelled'}), 400
        
        # Restore stock for all items
        for item in order.items:
            item.product.increase_stock(item.quantity)
        
        # Update order status
        order.update_status(Order.STATUS_CANCELLED)
        
        db.session.commit()
        
        return jsonify({'message': 'Order cancelled successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/statuses', methods=['GET'])
def get_order_statuses():
    """Get available order statuses."""
    return jsonify({
        'statuses': Order.VALID_STATUSES
    })

@bp.route('/stats', methods=['GET'])
def get_order_stats():
    """Get order statistics."""
    try:
        total_orders = Order.query.count()
        
        # Orders by status
        status_stats = db.session.query(
            Order.status,
            db.func.count(Order.id).label('count')
        ).group_by(Order.status).all()
        
        # Total revenue
        total_revenue = db.session.query(
            db.func.sum(Order.total_amount)
        ).filter(Order.status != Order.STATUS_CANCELLED).scalar() or 0
        
        # Average order value
        avg_order_value = db.session.query(
            db.func.avg(Order.total_amount)
        ).filter(Order.status != Order.STATUS_CANCELLED).scalar() or 0
        
        return jsonify({
            'total_orders': total_orders,
            'by_status': {status: count for status, count in status_stats},
            'total_revenue': float(total_revenue),
            'average_order_value': float(avg_order_value)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/recent', methods=['GET'])
def get_recent_orders():
    """Get recent orders (last 10)."""
    try:
        orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
        return jsonify({
            'orders': [order.to_dict() for order in orders]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500 