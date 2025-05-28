import numpy as np

def create_mappings(df):
    users = df['customer_id'].unique()
    products = df['product_id'].unique()

    user_to_idx = {user: idx for idx, user in enumerate(users)}
    product_to_idx = {prod: idx for idx, prod in enumerate(products)}

    idx_to_product = {idx: prod for prod, idx in product_to_idx.items()}

    return user_to_idx, product_to_idx, idx_to_product

def build_interaction_matrix(df, user_to_idx, product_to_idx):
    num_users = len(user_to_idx)
    num_products = len(product_to_idx)

    R = np.zeros((num_users, num_products))
    for _, row in df.iterrows():
        user_id = row.get('customer_id') or row.get('user_id')
        product_id = row['product_id']
        if user_id in user_to_idx and product_id in product_to_idx:
            u = user_to_idx[user_id]
            p = product_to_idx[product_id]
            R[u, p] = 1
    return R