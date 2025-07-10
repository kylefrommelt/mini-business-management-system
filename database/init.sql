-- Mini Business Management System Database Schema
-- This script initializes the database with sample data for demonstration

-- Note: Database creation is handled by Docker Compose
-- This script runs within the bizowie_erp database

-- Create tables (SQLAlchemy will handle this, but having schema for reference)
-- This serves as documentation of the database structure

-- Customers table
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    phone VARCHAR(20),
    company VARCHAR(100),
    address TEXT,
    city VARCHAR(50),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    country VARCHAR(50) DEFAULT 'USA',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    tier VARCHAR(20) DEFAULT 'Standard'
);

-- Products table
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    sku VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    cost DECIMAL(10, 2),
    stock_quantity INTEGER DEFAULT 0,
    low_stock_threshold INTEGER DEFAULT 10,
    reorder_point INTEGER DEFAULT 20,
    weight DECIMAL(8, 2),
    dimensions VARCHAR(50),
    color VARCHAR(30),
    size VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Orders table
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    order_number VARCHAR(20) UNIQUE NOT NULL,
    customer_id INTEGER REFERENCES customers(id),
    status VARCHAR(20) DEFAULT 'Pending',
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    shipping_address TEXT,
    shipping_city VARCHAR(50),
    shipping_state VARCHAR(2),
    shipping_zip VARCHAR(10),
    shipping_country VARCHAR(50) DEFAULT 'USA',
    subtotal DECIMAL(10, 2) DEFAULT 0.00,
    tax_amount DECIMAL(10, 2) DEFAULT 0.00,
    shipping_amount DECIMAL(10, 2) DEFAULT 0.00,
    total_amount DECIMAL(10, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    shipped_date TIMESTAMP,
    delivered_date TIMESTAMP
);

-- Order items table
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    line_total DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_orders_number ON orders(order_number);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);

-- Insert sample data for demonstration
-- Sample customers
INSERT INTO customers (first_name, last_name, email, phone, company, address, city, state, zip_code, tier) VALUES
('John', 'Doe', 'john.doe@example.com', '555-0101', 'Acme Corp', '123 Main St', 'Pittsburgh', 'PA', '15201', 'Premium'),
('Jane', 'Smith', 'jane.smith@example.com', '555-0102', 'TechStart Inc', '456 Oak Ave', 'Pittsburgh', 'PA', '15202', 'Standard'),
('Bob', 'Johnson', 'bob.johnson@example.com', '555-0103', 'Manufacturing Co', '789 Pine Rd', 'Pittsburgh', 'PA', '15203', 'Enterprise'),
('Alice', 'Wilson', 'alice.wilson@example.com', '555-0104', 'Retail Solutions', '321 Elm St', 'Pittsburgh', 'PA', '15204', 'Standard'),
('Charlie', 'Brown', 'charlie.brown@example.com', '555-0105', 'Brown Industries', '654 Maple Dr', 'Pittsburgh', 'PA', '15205', 'Premium')
ON CONFLICT (email) DO NOTHING;

-- Sample products
INSERT INTO products (name, sku, description, category, price, cost, stock_quantity, low_stock_threshold, reorder_point, weight, dimensions, color, size) VALUES
('Wireless Headphones', 'WH-001', 'High-quality wireless headphones with noise cancellation', 'Electronics', 299.99, 150.00, 45, 10, 20, 0.8, '8x7x3', 'Black', 'M'),
('Office Chair', 'OC-002', 'Ergonomic office chair with lumbar support', 'Furniture', 199.99, 80.00, 25, 5, 15, 25.5, '26x26x42', 'Black', 'Standard'),
('Laptop Stand', 'LS-003', 'Adjustable laptop stand for better ergonomics', 'Electronics', 49.99, 20.00, 75, 15, 30, 2.1, '12x10x2', 'Silver', 'Universal'),
('Coffee Mug', 'CM-004', 'Ceramic coffee mug with company logo', 'Merchandise', 12.99, 5.00, 150, 25, 50, 0.6, '4x4x4', 'White', '12oz'),
('Desk Lamp', 'DL-005', 'LED desk lamp with adjustable brightness', 'Electronics', 79.99, 35.00, 35, 8, 18, 3.2, '6x6x18', 'White', 'Standard'),
('Notebook Set', 'NS-006', 'Set of 3 professional notebooks', 'Stationery', 24.99, 8.00, 200, 40, 80, 1.5, '8x11x1', 'Blue', 'A4'),
('Wireless Mouse', 'WM-007', 'Ergonomic wireless mouse with precision tracking', 'Electronics', 59.99, 25.00, 8, 10, 25, 0.3, '5x3x1', 'Black', 'Standard'),
('Plant Pot', 'PP-008', 'Decorative ceramic plant pot for office plants', 'Decor', 29.99, 12.00, 60, 12, 25, 2.8, '6x6x8', 'Green', 'Medium')
ON CONFLICT (sku) DO NOTHING;

-- Sample orders
INSERT INTO orders (order_number, customer_id, status, shipping_address, shipping_city, shipping_state, shipping_zip, subtotal, tax_amount, shipping_amount, total_amount) VALUES
('ORD001', 1, 'Delivered', '123 Main St', 'Pittsburgh', 'PA', '15201', 349.98, 27.99, 9.99, 387.96),
('ORD002', 2, 'Shipped', '456 Oak Ave', 'Pittsburgh', 'PA', '15202', 199.99, 15.99, 9.99, 225.97),
('ORD003', 3, 'Processing', '789 Pine Rd', 'Pittsburgh', 'PA', '15203', 129.98, 10.39, 9.99, 150.36),
('ORD004', 4, 'Pending', '321 Elm St', 'Pittsburgh', 'PA', '15204', 59.99, 4.79, 9.99, 74.77),
('ORD005', 5, 'Delivered', '654 Maple Dr', 'Pittsburgh', 'PA', '15205', 104.98, 8.39, 9.99, 123.36)
ON CONFLICT (order_number) DO NOTHING;

-- Sample order items
INSERT INTO order_items (order_id, product_id, quantity, unit_price, line_total) VALUES
(1, 1, 1, 299.99, 299.99),
(1, 3, 1, 49.99, 49.99),
(2, 2, 1, 199.99, 199.99),
(3, 4, 5, 12.99, 64.95),
(3, 5, 1, 79.99, 79.99),
(4, 7, 1, 59.99, 59.99),
(5, 6, 2, 24.99, 49.98),
(5, 8, 1, 29.99, 29.99),
(5, 4, 2, 12.99, 25.98)
ON CONFLICT DO NOTHING;

-- Update updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres; 