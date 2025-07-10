"""
Customer Model - CRM functionality
"""
from datetime import datetime
from backend.app import db


class Customer(db.Model):
    """Customer model representing clients in the CRM system."""
    
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    company = db.Column(db.String(100), nullable=True)
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(50), nullable=True)
    state = db.Column(db.String(2), nullable=True)
    zip_code = db.Column(db.String(10), nullable=True)
    country = db.Column(db.String(50), default='USA')
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Customer tier for business logic
    tier = db.Column(db.String(20), default='Standard')  # Standard, Premium, Enterprise
    
    # Relationships
    orders = db.relationship('Order', backref='customer', lazy=True)
    
    def __repr__(self):
        return f'<Customer {self.first_name} {self.last_name} ({self.email})>'
    
    @property
    def full_name(self):
        """Return customer's full name."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_address(self):
        """Return formatted full address."""
        parts = [self.address, self.city, self.state, self.zip_code, self.country]
        return ', '.join(part for part in parts if part)
    
    def to_dict(self):
        """Convert customer to dictionary for API responses."""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'company': self.company,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'country': self.country,
            'full_address': self.full_address,
            'tier': self.tier,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'order_count': len(self.orders)
        } 