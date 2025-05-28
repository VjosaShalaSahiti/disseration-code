from flask import Flask, request, jsonify
from database.populate import fetch_shopify_data, save_data_to_db
from database.database import get_connection
from recommender.hybrid_recommender import hybrid_recommend
from utils.mappings import create_mappings, build_interaction_matrix
from model.matrix_factorization import MatrixFactorization
import pandas as pd
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 

@app.route("/sync", methods=["POST"])
def sync_store_data():
    data = request.json
    shop_domain = data.get("shop_domain")
    access_token = data.get("access_token")

    if not shop_domain or not access_token:
        return jsonify({"error": "Missing shop_domain or access_token"}), 400

    try:
        orders, products = fetch_shopify_data(shop_domain, access_token)
        save_data_to_db(orders, products, shop_domain, access_token)
        return jsonify({
            "message": "Store data synced successfully.",
            "orders_count": len(orders),
            "products_count": len(products)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.json
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "Missing user_id in request"}), 400

    try:
        conn = get_connection()
        orders_df = pd.read_sql("SELECT customer_id, product_id FROM orders", conn)
        metadata_df = pd.read_sql("SELECT product_id AS product_id, title, category, tags, type FROM products", conn)
        conn.close()

        user_to_idx, product_to_idx, idx_to_product = create_mappings(orders_df)
        R = build_interaction_matrix(orders_df, user_to_idx, product_to_idx)

        mf = MatrixFactorization(R=R, K=10, alpha=0.01, beta=0.01, iterations=50)
        mf.train()

        transactions = (
            orders_df.groupby('customer_id')['product_id']
            .apply(lambda x: list(x) if isinstance(x, pd.Series) else [x])
            .tolist()
        )

        recommendations = hybrid_recommend(
            user_id=user_id,
            matrix_model=mf,
            content_model_data=metadata_df,
            transactions=transactions,
            user_to_idx=user_to_idx,
            idx_to_product=idx_to_product,
            df=orders_df,
            top_n=3
        )

        return jsonify({"recommendations": recommendations}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/interact", methods=["POST"])
def update_after_interaction():
    data = request.json
    user_id = data.get("user_id")
    product_ids = data.get("product_ids")

    if not user_id or not product_ids:
        return jsonify({"error": "Missing user_id or product_ids"}), 400

    orders_df = pd.read_sql("SELECT customer_id, product_id FROM orders", get_connection())
    user_to_idx, product_to_idx, _ = create_mappings(orders_df)
    R = build_interaction_matrix(orders_df, user_to_idx, product_to_idx)

    mf = MatrixFactorization(R=R, K=10, alpha=0.01, beta=0.01, iterations=100)
    mf.load_factors_from_db(user_to_idx, product_to_idx)
    mf.update_user_vector(user_id, product_ids, user_to_idx, product_to_idx)

    return jsonify({"message": "User vector updated successfully."})

@app.route("/uninstall", methods=["POST"])
def uninstall_store():
    data = request.json
    shop_domain = data.get("shop_domain")

    if not shop_domain:
        return jsonify({"error": "Missing shop_domain"}), 400

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT store_id FROM stores WHERE shop_domain = %s", (shop_domain,))
        result = cur.fetchone()
        if not result:
            return jsonify({"message": "Store not found."}), 404
        store_id = result[0]

        cur.execute("DELETE FROM orders WHERE store_id = %s", (store_id,))
        cur.execute("DELETE FROM products WHERE product_id IN (SELECT product_id FROM orders WHERE store_id = %s)", (store_id,))
        cur.execute("DELETE FROM user_factors WHERE user_id IN (SELECT customer_id FROM orders WHERE store_id = %s)", (store_id,))
        cur.execute("DELETE FROM item_factors WHERE product_id IN (SELECT product_id FROM orders WHERE store_id = %s)", (store_id,))
        cur.execute("DELETE FROM stores WHERE store_id = %s", (store_id,))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": f"All data for {shop_domain} deleted successfully."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/order", methods=["POST"])
def add_order_and_update_user_vector():
    data = request.json
    customer_id = data.get("customer_id")
    product_ids = data.get("product_ids")
    order_id = data.get("order_id")
    order_date = data.get("order_date", datetime.utcnow().isoformat())
    store_domain = data.get("shop_domain")

    if not customer_id or not product_ids or not order_id or not store_domain:
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT store_id FROM stores WHERE shop_domain = %s", (store_domain,))
    result = cur.fetchone()
    if not result:
        return jsonify({"error": "Store not found"}), 404
    store_id = result[0]

    cur.execute("INSERT INTO customers (customer_id) VALUES (%s) ON CONFLICT DO NOTHING", (customer_id,))

    for product_id in product_ids:
        cur.execute("""
            INSERT INTO orders (store_id, order_id, product_id, customer_id, order_date)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (store_id, order_id, product_id, customer_id, order_date))

    conn.commit()
    cur.close()
    conn.close()

    orders_df = pd.read_sql("SELECT customer_id, product_id FROM orders", get_connection())
    user_to_idx, product_to_idx, idx_to_product = create_mappings(orders_df)
    R = build_interaction_matrix(orders_df, user_to_idx, product_to_idx)

    mf = MatrixFactorization(R=R, K=10, alpha=0.01, beta=0.01, iterations=100)
    mf.load_factors_from_db(user_to_idx, product_to_idx)
    mf.update_user_vector(customer_id, product_ids, user_to_idx, product_to_idx)

    return jsonify({"message": "Order stored and user vector updated."})

@app.route("/click", methods=["POST"])
def track_recommendation_click():
    data = request.json
    user_id = data.get("user_id")
    product_id = data.get("product_id")
    source = data.get("source", "unknown")

    if not user_id or not product_id:
        return jsonify({"error": "Missing user_id or product_id"}), 400

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO recommendation_clicks (user_id, product_id, source)
        VALUES (%s, %s, %s)
    """, (user_id, product_id, source))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Click tracked successfully."})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
