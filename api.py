import requests
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()
import os


ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
SHOP_NAME = os.getenv('SHOP_NAME')

API_VERSION = "2024-10" 


# GraphQL Endpoint
GRAPHQL_URL = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/graphql.json"

# GraphQL Query
query = """
query productImages {
  products(first: 20) {
    edges {
      node {
        id
        title
        images(first: 20) {
          edges {
            node {
              id
              altText
              src
            }
          }
        }
      }
    }
  }
}
"""

# Headers with Authorization
headers = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": ACCESS_TOKEN
}

# Make the Request
response = requests.post(
    GRAPHQL_URL,
    json={"query": query},
    headers=headers
)

# Check Response
if response.status_code == 200:
    data = response.json()
    print("GraphQL Query Response:")
    print(data)
else:
    print(f"Error: {response.status_code}")
    print(response.text)



save_directory = "product_images"
os.makedirs(save_directory, exist_ok=True)  # Create the directory if it doesn't exist

# Extract and loop through the products
products = data.get('data', {}).get('products', {}).get('edges', [])

for product in products:
    product_node = product.get('node', {})
    product_id = product_node.get('id').split('/')[-1]  # Extract numerical part of ID
    product_title = product_node.get('title')
    images = product_node.get('images', {}).get('edges', [])

    print(f"Processing Product ID: {product_id} ({product_title})")
    
    for idx, image in enumerate(images, start=1):
        image_node = image.get('node', {})
        image_url = image_node.get('src')
        
        # Define the file name
        image_filename = os.path.join(save_directory, f"{product_id}_image_{idx}.jpg")
        
        # Download and save the image
        try:
            response = requests.get(image_url, stream=True)
            if response.status_code == 200:
                with open(image_filename, 'wb') as file:
                    for chunk in response.iter_content(1024):
                        file.write(chunk)
                print(f"  - Saved: {image_filename}")
            else:
                print(f"  - Failed to download {image_url} (status code: {response.status_code})")
        except Exception as e:
            print(f"  - Error downloading {image_url}: {e}")
