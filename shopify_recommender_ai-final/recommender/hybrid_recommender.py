from random import sample
from model.association_rules import association_based_recommendations
from model.content_based import content_based_recommendations

def hybrid_recommend(user_id, matrix_model, content_model_data, transactions, user_to_idx, idx_to_product, df, top_n=3):
    purchased_products = df[df['customer_id'] == user_id]['product_id'].tolist()

    # Matrix Factorization Recommendations
    if user_id in user_to_idx:
        user_idx = user_to_idx[user_id]
        preds = matrix_model.full_matrix()[user_idx]
        matrix_recs = [idx_to_product[idx] for idx in preds.argsort()[::-1] if idx_to_product[idx] not in purchased_products]
    else:
        matrix_recs = []

    # Content-Based Recommendations
    content_recs = content_based_recommendations(purchased_products, content_model_data)

    # Association Rule Recommendations
    assoc_recs = association_based_recommendations(set(purchased_products), transactions)

    # Combine all
    final = matrix_recs + content_recs + assoc_recs
    final = list(dict.fromkeys(final))  # Remove duplicates while preserving order

    # Fallback: If less than top_n products, fill from random available products
    available_products = set(content_model_data['product_id'].tolist()) - set(purchased_products) - set(final)
    additional_products = sample(list(available_products), min(top_n - len(final), len(available_products)))
    final += additional_products

    return final[:top_n]