# Mini Business Management System

A lightweight ERP-style application demonstrating core business management features including customer relationship management, inventory tracking, and order processing.

## 🚀 Technology Stack

- **Backend**: Python 3.9+ with Flask
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **API**: RESTful endpoints with JSON responses
- **Deployment**: Docker & Docker Compose
- **Testing**: pytest for backend testing

## 📋 Features

### Customer Management (CRM)
- Customer registration and profiles
- Contact information management
- Customer activity tracking
- Search and filtering capabilities

### Inventory Management
- Product catalog with categories
- Stock level tracking
- Inventory alerts for low stock
- Product search and filtering

### Order Processing
- Order creation and management
- Order status tracking (Pending → Processing → Shipped → Delivered)
- Customer order history
- Inventory integration (automatic stock updates)

### Analytics Dashboard
- Sales overview
- Inventory insights
- Customer metrics
- Order trends

## 🏗️ Architecture

```
├── backend/
│   ├── app/
│   │   ├── models/          # Database models
│   │   ├── routes/          # API endpoints
│   │   ├── services/        # Business logic
│   │   └── utils/           # Helper functions
│   ├── migrations/          # Database migrations
│   └── tests/              # Backend tests
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── templates/          # HTML templates
├── database/
│   └── init.sql           # Database schema
└── docker-compose.yml      # Multi-container setup
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 13+
- Docker & Docker Compose (optional)

### Local Development Setup

1. **Clone and Setup**
   ```bash
   cd bizowie-portfolio-project
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Database Setup**
   ```bash
   # Create PostgreSQL database
   createdb bizowie_erp
   
   # Run migrations
   flask db upgrade
   ```

3. **Run Application**
   ```bash
   # Start backend
   python run.py
   
   # Access application at http://localhost:5000
   ```

### Docker Setup (Recommended)

```bash
# Start all services
docker-compose up -d

# Access application at http://localhost:5000
```

## 📊 API Endpoints

### Customers
- `GET /api/customers` - List all customers
- `POST /api/customers` - Create new customer
- `GET /api/customers/{id}` - Get customer details
- `PUT /api/customers/{id}` - Update customer
- `DELETE /api/customers/{id}` - Delete customer

### Products
- `GET /api/products` - List all products
- `POST /api/products` - Create new product
- `GET /api/products/{id}` - Get product details
- `PUT /api/products/{id}` - Update product
- `DELETE /api/products/{id}` - Delete product

### Orders
- `GET /api/orders` - List all orders
- `POST /api/orders` - Create new order
- `GET /api/orders/{id}` - Get order details
- `PUT /api/orders/{id}/status` - Update order status

### Analytics
- `GET /api/analytics/dashboard` - Dashboard metrics
- `GET /api/analytics/sales` - Sales analytics
- `GET /api/analytics/inventory` - Inventory analytics

## 🧪 Testing

```bash
# Run backend tests
pytest backend/tests/

# Run with coverage
pytest --cov=backend/app backend/tests/
```

## 📈 Project Highlights

This project demonstrates:

1. **Full-Stack Development**: Complete web application with separated concerns
2. **Database Design**: Normalized PostgreSQL schema with proper relationships
3. **REST API Development**: RESTful endpoints following best practices
4. **Modern JavaScript**: ES6+ features, async/await, DOM manipulation
5. **Responsive Design**: Mobile-first CSS with modern layout techniques
6. **Production Readiness**: Docker deployment, error handling, logging
7. **Testing**: Comprehensive test suite with pytest
8. **Documentation**: Clear API documentation and setup instructions

## 💼 Business Logic Implementation

- **Inventory Management**: Automatic stock updates when orders are placed
- **Order Workflow**: State machine pattern for order status transitions
- **Data Validation**: Server-side validation with meaningful error messages
- **Search & Filtering**: Advanced filtering capabilities across all entities
- **Analytics**: Real-time business metrics and insights

## 🔧 Configuration

Environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Flask secret key for sessions
- `DEBUG`: Enable debug mode (development only)
- `PORT`: Application port (default: 5000)

## 📝 Future Enhancements

- User authentication and authorization
- Email notifications for orders
- Advanced reporting features
- Integration with external APIs
- Mobile app development
- AWS deployment with RDS and EC2
