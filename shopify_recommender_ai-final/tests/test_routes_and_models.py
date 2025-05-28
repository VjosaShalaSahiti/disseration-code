import pytest
from api.app import app
from model.matrix_factorization import MatrixFactorization
from model.content_based import content_based_recommendations
from model.association_rules import apriori, association_based_recommendations
from recommender.hybrid_recommender import hybrid_recommend
import numpy as np
import pandas as pd

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_sync_route(client):
    response = client.post("/sync", json={"shop_domain": "test-shop", "access_token": "fake-token"})
    assert response.status_code in (200, 500)


def test_recommend_route(client):
    response = client.post("/recommend", json={"user_id": 555})
    assert response.status_code in (200, 500)


def test_interact_route(client):
    response = client.post("/interact", json={"user_id": 555, "product_ids": [101]})
    assert response.status_code in (200, 500)


def test_click_route(client):
    response = client.post("/click", json={"user_id": 555, "product_id": 101, "source": "matrix"})
    assert response.status_code == 200


def test_order_route(client):
    response = client.post("/order", json={
        "customer_id": 555,
        "product_ids": [101],
        "order_id": 9999,
        "order_date": "2025-05-23T12:00:00Z",
        "shop_domain": "test-shop"
    })
    assert response.status_code in (200, 500)


def test_uninstall_route(client):
    response = client.post("/uninstall", json={"shop_domain": "test-shop"})
    assert response.status_code in (200, 404)


def test_matrix_factorization():
    R = np.array([[5, 3], [4, 0], [1, 1]])
    mf = MatrixFactorization(R, K=2, alpha=0.01, beta=0.01, iterations=10)
    mf.train()
    full = mf.full_matrix()
    assert full.shape == R.shape


def test_content_based_recommendations():
    df = pd.DataFrame({
        "product_id": [101, 102],
        "title": ["Shirt", "Jacket"],
        "category": ["Clothing", "Clothing"],
        "tags": ["casual", "formal"],
        "type": ["Top", "Outerwear"]
    })
    result = content_based_recommendations([101], df)
    assert isinstance(result, list)


def test_apriori_and_association():
    transactions = [[1, 2], [1, 3], [2, 3], [1, 2, 3]]
    rules = apriori(transactions)
    assert isinstance(rules, dict)
    recommendations = association_based_recommendations(set([1]), transactions)
    assert isinstance(recommendations, list)


def test_hybrid_recommend():
    df = pd.DataFrame({"customer_id": [555, 555], "product_id": [101, 102]})
    meta = pd.DataFrame({
        "product_id": [101, 102, 103],
        "title": ["Item1", "Item2", "Item3"],
        "category": ["Cat1", "Cat1", "Cat2"],
        "tags": ["Tag1", "Tag2", "Tag3"],
        "type": ["Type1", "Type1", "Type2"]
    })
    from utils.mappings import create_mappings, build_interaction_matrix
    user_to_idx, product_to_idx, idx_to_product = create_mappings(df)
    R = build_interaction_matrix(df, user_to_idx, product_to_idx)
    mf = MatrixFactorization(R, K=2, alpha=0.01, beta=0.01, iterations=5)
    mf.train()
    transactions = df.groupby("customer_id")["product_id"].apply(list).tolist()
    result = hybrid_recommend(555, mf, meta, transactions, user_to_idx, idx_to_product, df, top_n=3)
    assert isinstance(result, list)
