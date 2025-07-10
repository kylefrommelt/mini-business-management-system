"""
Analytics Routes - REST API endpoints for business intelligence and reporting
"""
from flask import Blueprint, request, jsonify
from backend.app import db
from backend.app.models import Customer, Product, Order, OrderItem
from sqlalchemy import func, extract
from datetime import datetime, timedelta

bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

@bp.route('/dashboard', methods=['GET'])
def get_dashboard_metrics():
    """Get key metrics for the dashboard."""
    try:
        # Basic counts
        total_customers = Customer.query.filter(Customer.is_active == True).count()
        total_products = Product.query.filter(Product.is_active == True).count()
        total_orders = Order.query.count()
        
        # Revenue metrics
        total_revenue = db.session.query(
            func.sum(Order.total_amount)
        ).filter(Order.status != Order.STATUS_CANCELLED).scalar() or 0
        
        # This month's revenue
        current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_revenue = db.session.query(
            func.sum(Order.total_amount)
        ).filter(
            Order.order_date >= current_month_start,
            Order.status != Order.STATUS_CANCELLED
        ).scalar() or 0
        
        # Pending orders
        pending_orders = Order.query.filter(Order.status == Order.STATUS_PENDING).count()
        
        # Low stock products
        low_stock_products = Product.query.filter(
            Product.is_active == True,
            Product.stock_quantity <= Product.low_stock_threshold
        ).count()
        
        # Recent orders (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_orders = Order.query.filter(Order.order_date >= week_ago).count()
        
        return jsonify({
            'overview': {
                'total_customers': total_customers,
                'total_products': total_products,
                'total_orders': total_orders,
                'pending_orders': pending_orders,
                'low_stock_products': low_stock_products,
                'recent_orders': recent_orders
            },
            'revenue': {
                'total_revenue': float(total_revenue),
                'monthly_revenue': float(monthly_revenue)
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/sales', methods=['GET'])
def get_sales_analytics():
    """Get sales analytics and trends."""
    try:
        period = request.args.get('period', 'monthly')  # daily, weekly, monthly, yearly
        
        if period == 'daily':
            # Last 30 days
            date_trunc = func.date_trunc('day', Order.order_date)
            start_date = datetime.now() - timedelta(days=30)
        elif period == 'weekly':
            # Last 12 weeks
            date_trunc = func.date_trunc('week', Order.order_date)
            start_date = datetime.now() - timedelta(weeks=12)
        elif period == 'monthly':
            # Last 12 months
            date_trunc = func.date_trunc('month', Order.order_date)
            start_date = datetime.now() - timedelta(days=365)
        else:  # yearly
            date_trunc = func.date_trunc('year', Order.order_date)
            start_date = datetime.now() - timedelta(days=365 * 3)
        
        # Sales over time
        sales_data = db.session.query(
            date_trunc.label('period'),
            func.sum(Order.total_amount).label('revenue'),
            func.count(Order.id).label('order_count')
        ).filter(
            Order.order_date >= start_date,
            Order.status != Order.STATUS_CANCELLED
        ).group_by(date_trunc).order_by(date_trunc).all()
        
        # Top selling products
        top_products = db.session.query(
            Product.name,
            Product.sku,
            func.sum(OrderItem.quantity).label('total_sold'),
            func.sum(OrderItem.line_total).label('total_revenue')
        ).join(OrderItem).join(Order).filter(
            Order.order_date >= start_date,
            Order.status != Order.STATUS_CANCELLED
        ).group_by(Product.id, Product.name, Product.sku).order_by(
            func.sum(OrderItem.quantity).desc()
        ).limit(10).all()
        
        # Customer segments
        customer_segments = db.session.query(
            Customer.tier,
            func.count(Customer.id).label('customer_count'),
            func.sum(Order.total_amount).label('total_revenue')
        ).join(Order).filter(
            Order.order_date >= start_date,
            Order.status != Order.STATUS_CANCELLED
        ).group_by(Customer.tier).all()
        
        return jsonify({
            'sales_trend': [{
                'period': period_data[0].isoformat() if period_data[0] else None,
                'revenue': float(period_data[1]) if period_data[1] else 0,
                'orders': period_data[2] if period_data[2] else 0
            } for period_data in sales_data],
            'top_products': [{
                'name': product[0],
                'sku': product[1],
                'quantity_sold': product[2],
                'revenue': float(product[3])
            } for product in top_products],
            'customer_segments': [{
                'tier': segment[0],
                'customer_count': segment[1],
                'revenue': float(segment[2])
            } for segment in customer_segments]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/inventory', methods=['GET'])
def get_inventory_analytics():
    """Get inventory analytics and insights."""
    try:
        # Inventory value by category
        category_value = db.session.query(
            Product.category,
            func.sum(Product.price * Product.stock_quantity).label('inventory_value'),
            func.sum(Product.stock_quantity).label('total_units'),
            func.count(Product.id).label('product_count')
        ).filter(Product.is_active == True).group_by(Product.category).all()
        
        # Low stock alerts
        low_stock_products = db.session.query(
            Product.name,
            Product.sku,
            Product.stock_quantity,
            Product.low_stock_threshold,
            Product.category,
            Product.price
        ).filter(
            Product.is_active == True,
            Product.stock_quantity <= Product.low_stock_threshold
        ).all()
        
        # Reorder recommendations
        reorder_products = db.session.query(
            Product.name,
            Product.sku,
            Product.stock_quantity,
            Product.reorder_point,
            Product.category,
            Product.price
        ).filter(
            Product.is_active == True,
            Product.stock_quantity <= Product.reorder_point
        ).all()
        
        # Fast-moving products (high turnover)
        fast_movers = db.session.query(
            Product.name,
            Product.sku,
            Product.stock_quantity,
            func.sum(OrderItem.quantity).label('total_sold')
        ).join(OrderItem).join(Order).filter(
            Order.order_date >= datetime.now() - timedelta(days=30),
            Order.status != Order.STATUS_CANCELLED
        ).group_by(Product.id, Product.name, Product.sku, Product.stock_quantity).order_by(
            func.sum(OrderItem.quantity).desc()
        ).limit(10).all()
        
        return jsonify({
            'inventory_by_category': [{
                'category': cat[0],
                'inventory_value': float(cat[1]) if cat[1] else 0,
                'total_units': cat[2] if cat[2] else 0,
                'product_count': cat[3]
            } for cat in category_value],
            'low_stock_alerts': [{
                'name': product[0],
                'sku': product[1],
                'current_stock': product[2],
                'threshold': product[3],
                'category': product[4],
                'value': float(product[5]) if product[5] else 0
            } for product in low_stock_products],
            'reorder_recommendations': [{
                'name': product[0],
                'sku': product[1],
                'current_stock': product[2],
                'reorder_point': product[3],
                'category': product[4],
                'value': float(product[5]) if product[5] else 0
            } for product in reorder_products],
            'fast_movers': [{
                'name': product[0],
                'sku': product[1],
                'current_stock': product[2],
                'sold_last_30_days': product[3]
            } for product in fast_movers]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/customers', methods=['GET'])
def get_customer_analytics():
    """Get customer analytics and insights."""
    try:
        # Customer acquisition over time (monthly)
        acquisition_data = db.session.query(
            func.date_trunc('month', Customer.created_at).label('month'),
            func.count(Customer.id).label('new_customers')
        ).filter(
            Customer.created_at >= datetime.now() - timedelta(days=365)
        ).group_by(func.date_trunc('month', Customer.created_at)).order_by(
            func.date_trunc('month', Customer.created_at)
        ).all()
        
        # Top customers by revenue
        top_customers = db.session.query(
            Customer.first_name,
            Customer.last_name,
            Customer.email,
            Customer.tier,
            func.sum(Order.total_amount).label('total_spent'),
            func.count(Order.id).label('order_count')
        ).join(Order).filter(
            Order.status != Order.STATUS_CANCELLED
        ).group_by(
            Customer.id, Customer.first_name, Customer.last_name, Customer.email, Customer.tier
        ).order_by(func.sum(Order.total_amount).desc()).limit(10).all()
        
        # Customer distribution by tier
        tier_distribution = db.session.query(
            Customer.tier,
            func.count(Customer.id).label('count'),
            func.avg(Order.total_amount).label('avg_order_value')
        ).join(Order).filter(
            Customer.is_active == True,
            Order.status != Order.STATUS_CANCELLED
        ).group_by(Customer.tier).all()
        
        # Customer lifetime value segments
        clv_segments = db.session.query(
            func.sum(Order.total_amount).label('total_spent'),
            func.count(func.distinct(Customer.id)).label('customer_count')
        ).join(Customer).filter(
            Order.status != Order.STATUS_CANCELLED
        ).group_by(Customer.id).subquery()
        
        return jsonify({
            'acquisition_trend': [{
                'month': acq[0].isoformat() if acq[0] else None,
                'new_customers': acq[1]
            } for acq in acquisition_data],
            'top_customers': [{
                'name': f"{customer[0]} {customer[1]}",
                'email': customer[2],
                'tier': customer[3],
                'total_spent': float(customer[4]),
                'order_count': customer[5]
            } for customer in top_customers],
            'tier_distribution': [{
                'tier': tier[0],
                'customer_count': tier[1],
                'avg_order_value': float(tier[2]) if tier[2] else 0
            } for tier in tier_distribution]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/orders', methods=['GET'])
def get_order_analytics():
    """Get order analytics and trends."""
    try:
        # Order status distribution
        status_distribution = db.session.query(
            Order.status,
            func.count(Order.id).label('count'),
            func.avg(Order.total_amount).label('avg_value')
        ).group_by(Order.status).all()
        
        # Order fulfillment times (for completed orders)
        fulfillment_times = db.session.query(
            func.extract('epoch', Order.delivered_date - Order.order_date).label('fulfillment_seconds'),
            Order.total_amount
        ).filter(
            Order.status == Order.STATUS_DELIVERED,
            Order.delivered_date.isnot(None)
        ).all()
        
        # Average fulfillment time in days
        avg_fulfillment_days = None
        if fulfillment_times:
            avg_seconds = sum(ft[0] for ft in fulfillment_times if ft[0]) / len(fulfillment_times)
            avg_fulfillment_days = avg_seconds / (24 * 60 * 60)  # Convert to days
        
        # Order value distribution
        order_values = db.session.query(Order.total_amount).filter(
            Order.status != Order.STATUS_CANCELLED
        ).all()
        
        value_ranges = {
            '0-50': 0,
            '50-100': 0,
            '100-250': 0,
            '250-500': 0,
            '500+': 0
        }
        
        for order in order_values:
            value = float(order[0])
            if value < 50:
                value_ranges['0-50'] += 1
            elif value < 100:
                value_ranges['50-100'] += 1
            elif value < 250:
                value_ranges['100-250'] += 1
            elif value < 500:
                value_ranges['250-500'] += 1
            else:
                value_ranges['500+'] += 1
        
        return jsonify({
            'status_distribution': [{
                'status': status[0],
                'count': status[1],
                'avg_value': float(status[2]) if status[2] else 0
            } for status in status_distribution],
            'fulfillment_metrics': {
                'avg_fulfillment_days': avg_fulfillment_days,
                'completed_orders': len(fulfillment_times)
            },
            'order_value_distribution': value_ranges
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500 