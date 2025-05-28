from database.database import get_orders, get_product_metadata
from utils.mappings import create_mappings, build_interaction_matrix
from model.matrix_factorization import MatrixFactorization
from recommender.hybrid_recommender import hybrid_recommend

# Load data
orders_df = get_orders()
metadata_df = get_product_metadata()

# Build mappings
user_to_idx, product_to_idx, idx_to_product = create_mappings(orders_df)
R = build_interaction_matrix(orders_df, user_to_idx, product_to_idx)

# Train Matrix Factorization model
mf = MatrixFactorization(R=R, K=10, alpha=0.01, beta=0.01, iterations=100)
mf.train()

# Create transactions for Apriori
transactions = orders_df.groupby('customer_id')['product_name'].apply(lambda x: x.str.split(', ').sum()).tolist()

# Recommend
user_id = 1
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
