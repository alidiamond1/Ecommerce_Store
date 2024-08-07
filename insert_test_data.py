from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB Atlas connection
MONGODB_URI = os.getenv('MONGODB_URI')
client = MongoClient(MONGODB_URI)
db = client['ecommerce_db']

# Sample product data with image URLs
products = [
    {
        "name": "Smartphone",
        "description": "Latest model with high-resolution camera",
        "price": 699.99,
        "stock": 50,
        "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
    },
    {
        "name": "Laptop",
        "description": "Powerful laptop for work and gaming",
        "price": 1299.99,
        "stock": 30,
        "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
    },
    {
        "name": "Wireless Earbuds",
        "description": "True wireless earbuds with noise cancellation",
        "price": 149.99,
        "stock": 100,
        "image_url": "https://images.unsplash.com/photo-1590658006821-04f4008d5717?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
    },
    {
        "name": "Smart Watch",
        "description": "Fitness tracker and smartwatch in one",
        "price": 199.99,
        "stock": 75,
        "image_url": "https://images.unsplash.com/photo-1544117519-31a4b719223d?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
    },
    {
        "name": "4K TV",
        "description": "55-inch 4K Smart TV with HDR",
        "price": 599.99,
        "stock": 25,
        "image_url": "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
    }
]

# Clear existing products
db.products.delete_many({})

# Insert products into the database
result = db.products.insert_many(products)

print(f"Inserted {len(result.inserted_ids)} products into the database.")

# Verify insertion by querying the products
all_products = list(db.products.find())
print("\nProducts in the database:")
for product in all_products:
    print(f"- {product['name']}: ${product['price']}")

client.close()