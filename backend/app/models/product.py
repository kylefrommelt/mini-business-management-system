"""
Product Model - Inventory management functionality
"""
from datetime import datetime
from backend.app import db


class Product(db.Model):
    """Product model representing inventory items."""
    
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False)
    
    # Pricing
    price = db.Column(db.Numeric(10, 2), nullable=False)
    cost = db.Column(db.Numeric(10, 2), nullable=True)
    
    # Inventory tracking
    stock_quantity = db.Column(db.Integer, default=0)
    low_stock_threshold = db.Column(db.Integer, default=10)
    reorder_point = db.Column(db.Integer, default=20)
    
    # Product attributes
    weight = db.Column(db.Numeric(8, 2), nullable=True)  # in pounds
    dimensions = db.Column(db.String(50), nullable=True)  # LxWxH
    color = db.Column(db.String(30), nullable=True)
    size = db.Column(db.String(20), nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    
    def __repr__(self):
        return f'<Product {self.name} ({self.sku})>'
    
    @property
    def is_low_stock(self):
        """Check if product is below low stock threshold."""
        return self.stock_quantity <= self.low_stock_threshold
    
    @property
    def needs_reorder(self):
        """Check if product needs to be reordered."""
        return self.stock_quantity <= self.reorder_point
    
    @property
    def profit_margin(self):
        """Calculate profit margin if cost is available."""
        if self.cost and self.cost > 0:
            return float((self.price - self.cost) / self.price * 100)
        return None
    
    def reduce_stock(self, quantity):
        """Reduce stock quantity by specified amount."""
        if self.stock_quantity >= quantity:
            self.stock_quantity -= quantity
            return True
        return False
    
    def increase_stock(self, quantity):
        """Increase stock quantity by specified amount."""
        self.stock_quantity += quantity
    
    def to_dict(self):
        """Convert product to dictionary for API responses."""
        return {
            'id': self.id,
            'name': self.name,
            'sku': self.sku,
            'description': self.description,
            'category': self.category,
            'price': float(self.price) if self.price else None,
            'cost': float(self.cost) if self.cost else None,
            'stock_quantity': self.stock_quantity,
            'low_stock_threshold': self.low_stock_threshold,
            'reorder_point': self.reorder_point,
            'weight': float(self.weight) if self.weight else None,
            'dimensions': self.dimensions,
            'color': self.color,
            'size': self.size,
            'is_active': self.is_active,
            'is_low_stock': self.is_low_stock,
            'needs_reorder': self.needs_reorder,
            'profit_margin': self.profit_margin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 