import psycopg2
import pandas as pd
import requests
from config import Config
from database.database import get_connection

def fetch_shopify_data(shop_domain, access_token):
    headers = {"X-Shopify-Access-Token": access_token}
    orders_url = f"https://{shop_domain}/admin/api/2023-10/orders.json"
    products_url = f"https://{shop_domain}/admin/api/2023-10/products.json"

    orders_resp = requests.get(orders_url, headers=headers)
    products_resp = requests.get(products_url, headers=headers)

    return orders_resp.json().get("orders", []), products_resp.json().get("products", [])

def save_data_to_db(orders, products, shop_domain, access_token):
    conn = get_connection()
    cur = conn.cursor()

    # Insert store or get existing store_id
    cur.execute("""
        INSERT INTO stores (shop_domain, access_token)
        VALUES (%s, %s)
        ON CONFLICT (shop_domain) DO NOTHING
    """, (shop_domain, access_token))

    cur.execute("SELECT store_id FROM stores WHERE shop_domain = %s", (shop_domain,))
    result = cur.fetchone()
    store_id = result[0] if result else None

    # Insert products
    for product in products:
        cur.execute("""
            INSERT INTO products (product_id, handle, title, category, tags, type)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (product_id) DO NOTHING
        """, (
            product["id"],
            product["handle"],
            product["title"],
            product.get("product_type", "Unknown"),
            product.get("tags", ""),
            product.get("product_type", "Unknown")
        ))

    # Insert customers + orders
    for order in orders:
        customer = order.get("customer")
        if not customer:
            continue

        customer_id = customer["id"]
        cur.execute("INSERT INTO customers (customer_id) VALUES (%s) ON CONFLICT DO NOTHING", (customer_id,))

        for item in order.get("line_items", []):
            shopify_product_id = item.get("product_id")
            if not shopify_product_id:
                continue

            cur.execute("SELECT product_id FROM products WHERE product_id = %s", (shopify_product_id,))
            product = cur.fetchone()
            if not product:
                continue

            product_id = product[0]
            cur.execute("""
                INSERT INTO orders (store_id, order_id, product_id, customer_id, order_date)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (store_id, order["id"], product_id, customer_id, order["created_at"]))

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    shop_domain = Config.SHOP_DOMAIN
    access_token = Config.SHOPIFY_ADMIN_ACCESS_TOKEN
    orders, products = fetch_shopify_data(shop_domain, access_token)
    save_data_to_db(orders, products, shop_domain, access_token)