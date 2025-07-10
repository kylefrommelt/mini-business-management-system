"""
Order Models - Order processing workflow
"""
from datetime import datetime
from backend.app import db


class Order(db.Model):
    """Order model representing customer orders."""
    
    __tablename__ = 'orders'
    
    # Order states
    STATUS_PENDING = 'Pending'
    STATUS_PROCESSING = 'Processing'
    STATUS_SHIPPED = 'Shipped'
    STATUS_DELIVERED = 'Delivered'
    STATUS_CANCELLED = 'Cancelled'
    
    VALID_STATUSES = [
        STATUS_PENDING,
        STATUS_PROCESSING,
        STATUS_SHIPPED,
        STATUS_DELIVERED,
        STATUS_CANCELLED
    ]
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    
    # Order details
    status = db.Column(db.String(20), default=STATUS_PENDING, nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Shipping information
    shipping_address = db.Column(db.Text, nullable=True)
    shipping_city = db.Column(db.String(50), nullable=True)
    shipping_state = db.Column(db.String(2), nullable=True)
    shipping_zip = db.Column(db.String(10), nullable=True)
    shipping_country = db.Column(db.String(50), default='USA')
    
    # Order totals
    subtotal = db.Column(db.Numeric(10, 2), default=0.00)
    tax_amount = db.Column(db.Numeric(10, 2), default=0.00)
    shipping_amount = db.Column(db.Numeric(10, 2), default=0.00)
    total_amount = db.Column(db.Numeric(10, 2), default=0.00)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    shipped_date = db.Column(db.DateTime, nullable=True)
    delivered_date = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.order_number} - {self.status}>'
    
    def generate_order_number(self):
        """Generate a unique order number."""
        import random
        import string
        prefix = 'ORD'
        timestamp = str(int(datetime.utcnow().timestamp()))[-6:]
        random_part = ''.join(random.choices(string.digits, k=3))
        return f"{prefix}{timestamp}{random_part}"
    
    def can_transition_to(self, new_status):
        """Check if order can transition to new status."""
        valid_transitions = {
            self.STATUS_PENDING: [self.STATUS_PROCESSING, self.STATUS_CANCELLED],
            self.STATUS_PROCESSING: [self.STATUS_SHIPPED, self.STATUS_CANCELLED],
            self.STATUS_SHIPPED: [self.STATUS_DELIVERED],
            self.STATUS_DELIVERED: [],
            self.STATUS_CANCELLED: []
        }
        return new_status in valid_transitions.get(self.status, [])
    
    def update_status(self, new_status):
        """Update order status with validation."""
        if not self.can_transition_to(new_status):
            return False
        
        self.status = new_status
        self.updated_at = datetime.utcnow()
        
        # Set specific dates based on status
        if new_status == self.STATUS_SHIPPED:
            self.shipped_date = datetime.utcnow()
        elif new_status == self.STATUS_DELIVERED:
            self.delivered_date = datetime.utcnow()
        
        return True
    
    def calculate_totals(self):
        """Recalculate order totals based on items."""
        self.subtotal = sum(item.line_total for item in self.items)
        self.tax_amount = self.subtotal * 0.08  # 8% tax rate
        self.total_amount = self.subtotal + self.tax_amount + self.shipping_amount
    
    @property
    def full_shipping_address(self):
        """Return formatted shipping address."""
        parts = [
            self.shipping_address,
            self.shipping_city,
            self.shipping_state,
            self.shipping_zip,
            self.shipping_country
        ]
        return ', '.join(part for part in parts if part)
    
    def to_dict(self):
        """Convert order to dictionary for API responses."""
        return {
            'id': self.id,
            'order_number': self.order_number,
            'customer_id': self.customer_id,
            'status': self.status,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'shipping_address': self.shipping_address,
            'shipping_city': self.shipping_city,
            'shipping_state': self.shipping_state,
            'shipping_zip': self.shipping_zip,
            'shipping_country': self.shipping_country,
            'full_shipping_address': self.full_shipping_address,
            'subtotal': float(self.subtotal) if self.subtotal else 0.00,
            'tax_amount': float(self.tax_amount) if self.tax_amount else 0.00,
            'shipping_amount': float(self.shipping_amount) if self.shipping_amount else 0.00,
            'total_amount': float(self.total_amount) if self.total_amount else 0.00,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'shipped_date': self.shipped_date.isoformat() if self.shipped_date else None,
            'delivered_date': self.delivered_date.isoformat() if self.delivered_date else None,
            'items': [item.to_dict() for item in self.items]
        }


class OrderItem(db.Model):
    """Order item model representing individual products in an order."""
    
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    # Item details
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    line_total = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<OrderItem Order:{self.order_id} Product:{self.product_id} Qty:{self.quantity}>'
    
    def calculate_line_total(self):
        """Calculate line total based on quantity and unit price."""
        self.line_total = self.quantity * self.unit_price
    
    def to_dict(self):
        """Convert order item to dictionary for API responses."""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price) if self.unit_price else 0.00,
            'line_total': float(self.line_total) if self.line_total else 0.00,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'product': self.product.to_dict() if self.product else None
        } 