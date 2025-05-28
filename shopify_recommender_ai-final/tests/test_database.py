import pytest
from unittest.mock import patch
from database.database import (
    get_connection,
    get_orders,
    get_product_metadata,
    get_clicks
)
from database.populate import fetch_shopify_data, save_data_to_db


def test_get_connection():
    conn = get_connection()
    assert conn is not None
    assert conn.closed == 0
    conn.close()


def test_get_orders():
    df = get_orders()
    assert "customer_id" in df.columns
    assert "product_id" in df.columns


def test_get_product_metadata():
    df = get_product_metadata()
    assert "product_id" in df.columns
    assert "title" in df.columns


def test_get_clicks():
    df = get_clicks()
    assert "user_id" in df.columns
    assert "product_id" in df.columns


@patch("database.populate.requests.get")
def test_fetch_shopify_data(mock_get):
    mock_get.return_value.json.side_effect = [
        {"orders": [{"id": 1}]},
        {"products": [{"id": 101, "handle": "test-product"}]}
    ]
    orders, products = fetch_shopify_data("fake.myshopify.com", "fake-token")
    assert isinstance(orders, list)
    assert isinstance(products, list)
    assert orders[0]["id"] == 1
    assert products[0]["handle"] == "test-product"


def test_save_data_to_db_inserts_records():
    orders = [{
        "id": 111,
        "created_at": "2024-01-01T00:00:00Z",
        "customer": {"id": 555},
        "line_items": [{"product_id": 101}]
    }]
    products = [{
        "id": 101,
        "handle": "test-product",
        "title": "Test Product",
        "product_type": "Book",
        "tags": "tag1,tag2"
    }]
    save_data_to_db(orders, products, "test-shop", "test-token")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE order_id = 111")
    result = cur.fetchone()
    assert result is not None
    cur.close()
    conn.close()
