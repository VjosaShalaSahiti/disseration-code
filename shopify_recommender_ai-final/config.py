import os

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://vjosashala:password@localhost/shopify")
    SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY")
    SHOPIFY_API_SECRET = os.getenv("SHOPIFY_API_SECRET")
    SHOP_DOMAIN = os.getenv("SHOP_DOMAIN")
    SHOPIFY_ADMIN_ACCESS_TOKEN = os.getenv("SHOPIFY_ADMIN_ACCESS_TOKEN")
    SHOPIFY_API_VERSION = os.getenv("SHOPIFY_API_VERSION")

