# retrain.py – Periodically update user/item factors based on click data

from database.database import get_clicks
from utils.mappings import create_mappings, build_interaction_matrix
from model.matrix_factorization import MatrixFactorization

# Step 1: Load click data
click_df = get_clicks()

# Step 2: Generate mappings and interaction matrix
user_to_idx, product_to_idx, _ = create_mappings(click_df)
R = build_interaction_matrix(click_df, user_to_idx, product_to_idx)

# Step 3: Train Matrix Factorization model
mf = MatrixFactorization(R=R, K=10, alpha=0.01, beta=0.01, iterations=100)
mf.train()

# Step 4: Save updated user/item vectors
mf.save_factors_to_db(user_to_idx, product_to_idx)
