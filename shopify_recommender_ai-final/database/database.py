# database.py 
import psycopg2
import pandas as pd
from config import Config

def get_connection():
    return psycopg2.connect(Config.DATABASE_URL)

def get_orders():
    conn = get_connection()
    query = "SELECT customer_id, product_id FROM orders"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_product_metadata():
    conn = get_connection()
    query = "SELECT product_id, title, category, tags, type FROM products"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_clicks():
    conn = get_connection()
    query = "SELECT user_id, product_id FROM recommendation_clicks"
    df = pd.read_sql(query, conn)
    conn.close()
    return df