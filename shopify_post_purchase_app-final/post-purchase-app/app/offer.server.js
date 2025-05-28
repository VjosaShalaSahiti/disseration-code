const OFFERS = [];

/*
 * For testing purposes, product information is hardcoded.
 * In a production application, replace this function with logic to determine
 * what product to offer to the customer.
 */
export async function getOffers(userid) {
  try {
    // Step 1: Get recommended product IDs
    const recResponse = await fetch("https://b717-46-99-18-170.ngrok-free.app/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userid }),
    });

    if (!recResponse.ok) throw new Error("Failed to fetch recommendations");

    const recData = await recResponse.json();
    const ids = recData.recommendations;

    if (!ids || ids.length === 0) throw new Error("No recommendations returned");

    // Step 2: Convert to GIDs
    const gidArray = ids.map(id => `gid://shopify/Product/${id}`);

    // Step 3: GraphQL query for product data
    const gqlQuery = {
      query: `
        query getProducts($ids: [ID!]!) {
          nodes(ids: $ids) {
            ... on Product {
              id
              title
              featuredImage {
                url
              }
              variants(first: 1) {
                edges {
                  node {
                    id
                    price {
                      amount
                      currencyCode
                    }
                  }
                }
              }
            }
          }
        }
      `,
      variables: {
        ids: gidArray,
      },
    };

    // Step 4: Call Shopify Storefront API
    const productResponse = await fetch("https://test-vjosad.myshopify.com/api/2024-04/graphql.json", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Shopify-Storefront-Access-Token": "f2487671d4dcbd1f543079e061f808ba",
      },
      body: JSON.stringify(gqlQuery),
    });

    if (!productResponse.ok) throw new Error("Failed to fetch product data");

    const productData = await productResponse.json();
    const nodes = productData.data.nodes.filter(Boolean); // Remove nulls

    // Step 5: Map to OFFERS format
    const offers = nodes.map((product, index) => {
      const variant = product.variants.edges[0]?.node;
      if (!variant) return null; // skip if no variant

      return {
        id: index + 1,
        title: "One time offer",
        productTitle: product.title,
        productImageURL: product.featuredImage?.url || "https://cdn.shopify.com/static/images/examples/img-placeholder-1120x1120.png",
        productDescription: product.productDescription,
        originalPrice: variant.price.amount,
        discountedPrice: variant.price.amount,
        changes: [
          {
            type: "add_variant",
            variantID: String(variant.id.split("/").pop()),
            quantity: 1,
            discount: {
              value: 5,
              valueType: "percentage",
              title: "5% off",
            },
          },
        ],
      };
    }).filter(Boolean); // remove nulls

    return offers;

  } catch (error) {
    console.error("getOffers error:", error);
  }
}

/*
 * Retrieve discount information for the specific order on the backend instead of relying
 * on the discount information that is sent from the frontend.
 * This is to ensure that the discount information is not tampered with.
 */
export function getSelectedOffer(offerId) {
  return OFFERS.find((offer) => offer.id === offerId);
}