"""
Product Routes - REST API endpoints for inventory management
"""
from flask import Blueprint, request, jsonify
from backend.app import db
from backend.app.models import Product
from sqlalchemy import or_

bp = Blueprint('products', __name__, url_prefix='/api/products')

@bp.route('', methods=['GET'])
def get_products():
    """Get all products with optional filtering and pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        category = request.args.get('category', '')
        low_stock = request.args.get('low_stock', 'false').lower() == 'true'
        
        query = Product.query.filter(Product.is_active == True)
        
        # Apply search filter
        if search:
            query = query.filter(
                or_(
                    Product.name.ilike(f'%{search}%'),
                    Product.sku.ilike(f'%{search}%'),
                    Product.description.ilike(f'%{search}%')
                )
            )
        
        # Apply category filter
        if category:
            query = query.filter(Product.category == category)
        
        # Apply low stock filter
        if low_stock:
            query = query.filter(Product.stock_quantity <= Product.low_stock_threshold)
        
        # Pagination
        products = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'products': [product.to_dict() for product in products.items],
            'pagination': {
                'page': products.page,
                'pages': products.pages,
                'per_page': products.per_page,
                'total': products.total
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a specific product by ID."""
    try:
        product = Product.query.get_or_404(product_id)
        return jsonify(product.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@bp.route('', methods=['POST'])
def create_product():
    """Create a new product."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'sku', 'category', 'price']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if SKU already exists
        if Product.query.filter_by(sku=data['sku']).first():
            return jsonify({'error': 'SKU already exists'}), 400
        
        # Create product
        product = Product(
            name=data['name'],
            sku=data['sku'],
            description=data.get('description'),
            category=data['category'],
            price=data['price'],
            cost=data.get('cost'),
            stock_quantity=data.get('stock_quantity', 0),
            low_stock_threshold=data.get('low_stock_threshold', 10),
            reorder_point=data.get('reorder_point', 20),
            weight=data.get('weight'),
            dimensions=data.get('dimensions'),
            color=data.get('color'),
            size=data.get('size')
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify(product.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update an existing product."""
    try:
        product = Product.query.get_or_404(product_id)
        data = request.get_json()
        
        # Check if SKU is being changed and already exists
        if 'sku' in data and data['sku'] != product.sku:
            if Product.query.filter_by(sku=data['sku']).first():
                return jsonify({'error': 'SKU already exists'}), 400
        
        # Update product fields
        updateable_fields = [
            'name', 'sku', 'description', 'category', 'price', 'cost',
            'stock_quantity', 'low_stock_threshold', 'reorder_point',
            'weight', 'dimensions', 'color', 'size'
        ]
        
        for field in updateable_fields:
            if field in data:
                setattr(product, field, data[field])
        
        db.session.commit()
        
        return jsonify(product.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Soft delete a product (set is_active to False)."""
    try:
        product = Product.query.get_or_404(product_id)
        product.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Product deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:product_id>/stock', methods=['PUT'])
def update_stock(product_id):
    """Update product stock quantity."""
    try:
        product = Product.query.get_or_404(product_id)
        data = request.get_json()
        
        action = data.get('action')  # 'add' or 'subtract'
        quantity = data.get('quantity', 0)
        
        if not action or not quantity:
            return jsonify({'error': 'Action and quantity are required'}), 400
        
        if action == 'add':
            product.increase_stock(quantity)
        elif action == 'subtract':
            if not product.reduce_stock(quantity):
                return jsonify({'error': 'Insufficient stock'}), 400
        else:
            return jsonify({'error': 'Invalid action. Use "add" or "subtract"'}), 400
        
        db.session.commit()
        
        return jsonify(product.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all product categories."""
    try:
        categories = db.session.query(Product.category).filter(
            Product.is_active == True
        ).distinct().all()
        
        return jsonify({
            'categories': [category[0] for category in categories]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/low-stock', methods=['GET'])
def get_low_stock_products():
    """Get products with low stock."""
    try:
        products = Product.query.filter(
            Product.is_active == True,
            Product.stock_quantity <= Product.low_stock_threshold
        ).all()
        
        return jsonify({
            'products': [product.to_dict() for product in products],
            'count': len(products)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/reorder', methods=['GET'])
def get_reorder_products():
    """Get products that need reordering."""
    try:
        products = Product.query.filter(
            Product.is_active == True,
            Product.stock_quantity <= Product.reorder_point
        ).all()
        
        return jsonify({
            'products': [product.to_dict() for product in products],
            'count': len(products)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/stats', methods=['GET'])
def get_product_stats():
    """Get product statistics."""
    try:
        total_products = Product.query.filter(Product.is_active == True).count()
        low_stock_count = Product.query.filter(
            Product.is_active == True,
            Product.stock_quantity <= Product.low_stock_threshold
        ).count()
        
        # Products by category
        category_stats = db.session.query(
            Product.category,
            db.func.count(Product.id).label('count')
        ).filter(Product.is_active == True).group_by(Product.category).all()
        
        # Total inventory value
        total_value = db.session.query(
            db.func.sum(Product.price * Product.stock_quantity)
        ).filter(Product.is_active == True).scalar() or 0
        
        return jsonify({
            'total_products': total_products,
            'low_stock_products': low_stock_count,
            'by_category': {category: count for category, count in category_stats},
            'total_inventory_value': float(total_value)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500 