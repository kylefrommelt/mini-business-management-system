"""
Customer Routes - REST API endpoints for customer management
"""
from flask import Blueprint, request, jsonify
from backend.app import db
from backend.app.models import Customer
from sqlalchemy import or_

bp = Blueprint('customers', __name__, url_prefix='/api/customers')

@bp.route('', methods=['GET'])
def get_customers():
    """Get all customers with optional filtering and pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        tier = request.args.get('tier', '')
        
        query = Customer.query.filter(Customer.is_active == True)
        
        # Apply search filter
        if search:
            query = query.filter(
                or_(
                    Customer.first_name.ilike(f'%{search}%'),
                    Customer.last_name.ilike(f'%{search}%'),
                    Customer.email.ilike(f'%{search}%'),
                    Customer.company.ilike(f'%{search}%')
                )
            )
        
        # Apply tier filter
        if tier:
            query = query.filter(Customer.tier == tier)
        
        # Pagination
        customers = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'customers': [customer.to_dict() for customer in customers.items],
            'pagination': {
                'page': customers.page,
                'pages': customers.pages,
                'per_page': customers.per_page,
                'total': customers.total
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Get a specific customer by ID."""
    try:
        customer = Customer.query.get_or_404(customer_id)
        return jsonify(customer.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@bp.route('', methods=['POST'])
def create_customer():
    """Create a new customer."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if email already exists
        if Customer.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create customer
        customer = Customer(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data.get('phone'),
            company=data.get('company'),
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            zip_code=data.get('zip_code'),
            country=data.get('country', 'USA'),
            tier=data.get('tier', 'Standard')
        )
        
        db.session.add(customer)
        db.session.commit()
        
        return jsonify(customer.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    """Update an existing customer."""
    try:
        customer = Customer.query.get_or_404(customer_id)
        data = request.get_json()
        
        # Check if email is being changed and already exists
        if 'email' in data and data['email'] != customer.email:
            if Customer.query.filter_by(email=data['email']).first():
                return jsonify({'error': 'Email already exists'}), 400
        
        # Update customer fields
        updateable_fields = [
            'first_name', 'last_name', 'email', 'phone', 'company',
            'address', 'city', 'state', 'zip_code', 'country', 'tier'
        ]
        
        for field in updateable_fields:
            if field in data:
                setattr(customer, field, data[field])
        
        db.session.commit()
        
        return jsonify(customer.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    """Soft delete a customer (set is_active to False)."""
    try:
        customer = Customer.query.get_or_404(customer_id)
        customer.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Customer deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:customer_id>/orders', methods=['GET'])
def get_customer_orders(customer_id):
    """Get all orders for a specific customer."""
    try:
        customer = Customer.query.get_or_404(customer_id)
        orders = [order.to_dict() for order in customer.orders]
        
        return jsonify({
            'customer_id': customer_id,
            'customer_name': customer.full_name,
            'orders': orders
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/tiers', methods=['GET'])
def get_customer_tiers():
    """Get available customer tiers."""
    return jsonify({
        'tiers': ['Standard', 'Premium', 'Enterprise']
    })

@bp.route('/stats', methods=['GET'])
def get_customer_stats():
    """Get customer statistics."""
    try:
        total_customers = Customer.query.filter(Customer.is_active == True).count()
        
        # Customer by tier
        tier_stats = db.session.query(
            Customer.tier,
            db.func.count(Customer.id).label('count')
        ).filter(Customer.is_active == True).group_by(Customer.tier).all()
        
        return jsonify({
            'total_customers': total_customers,
            'by_tier': {tier: count for tier, count in tier_stats}
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500 