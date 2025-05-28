def content_based_recommendations(purchased_product_ids, product_metadata_df, top_n=3):
    if not purchased_product_ids:
        return []

    purchased = product_metadata_df[product_metadata_df['product_id'].isin(purchased_product_ids)]
    recommendations = product_metadata_df[
        (product_metadata_df['category'].isin(purchased['category'])) |
        (product_metadata_df['tags'].isin(purchased['tags'])) |
        (product_metadata_df['type'].isin(purchased['type']))
    ]

    recommendations = recommendations[~recommendations['product_id'].isin(purchased_product_ids)]
    return list(recommendations['product_id'].unique())[:top_n]
