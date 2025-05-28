-- Create stores table
CREATE TABLE IF NOT EXISTS stores (
    store_id SERIAL PRIMARY KEY,
    shop_domain TEXT UNIQUE,
    access_token TEXT
);

-- Create customers table
CREATE TABLE IF NOT EXISTS customers (
    customer_id BIGINT PRIMARY KEY,
    email TEXT,
    name TEXT
);

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    handle TEXT UNIQUE,
    title TEXT,
    category TEXT,
    tags TEXT,
    type TEXT
);

-- Create orders table
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    store_id INTEGER REFERENCES stores(store_id),
    order_id BIGINT,
    product_id INTEGER REFERENCES products(id),
    customer_id BIGINT REFERENCES customers(customer_id),
    order_date TIMESTAMP
);

-- Create user_factors table
CREATE TABLE IF NOT EXISTS user_factors (
    user_id BIGINT PRIMARY KEY,
    factors FLOAT8[]
);

-- Create item_factors table
CREATE TABLE IF NOT EXISTS item_factors (
    product_id INTEGER PRIMARY KEY,
    factors FLOAT8[]
);

-- Create recommendation_clicks table
CREATE TABLE IF NOT EXISTS recommendation_clicks (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES user_factors(user_id),
    product_id INTEGER REFERENCES products(id),
    clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source TEXT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_clicks_user_id ON recommendation_clicks(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_store_id ON orders(store_id);
CREATE INDEX IF NOT EXISTS idx_clicks_product_id ON recommendation_clicks(product_id);
