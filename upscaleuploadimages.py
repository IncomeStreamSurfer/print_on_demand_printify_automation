import requests
import pandas as pd
import base64
import os

# Set your API credentials 
access_token = "YOUR_PRINTIFY_API_KEY"

# Find your shop ID by running this: curl -X GET https://api.printify.com/v1/shops.json --header "Authorization: Bearer YOUR_PRINTIFY_API_KEY"

shop_id = "YOUR_SHOP_ID"

# Set the URL for the API endpoints
base_url = "https://api.printify.com/v1"
upload_url = f"{base_url}/uploads/images.json"
product_url = f"{base_url}/shops/{shop_id}/products.json"

# Load the CSV file
csv_path = "product_information.csv"  # Update this to your CSV file path
image_df = pd.read_csv(csv_path)

# Set headers for requests
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

for idx, row in image_df.iterrows():
    # Convert the image to Base64
    with open(row['local_path'], "rb") as img_file:
        img_b64 = base64.b64encode(img_file.read()).decode('utf-8')

    # Upload the image to the Printify media library
    data = {
        "file_name": row['file_name'],
        "contents": img_b64
    }
    response = requests.post(upload_url, headers=headers, json=data)
    image_id = response.json()["id"]

    # To change the print object, use this to find the variant id curl -X GET "https://api.printify.com/v1/catalog/blueprints/1098/print_providers/228/variants.json" "Authorization: Bearer YOUR_PRINTIFY_KEY"
   
   # Current settings are for wall art
   
    # Create the product with the uploaded image
    data = {
        "title": row['title'],
        "description": row['description'],
        "tags": row['tags'].split(', '),  # Assuming tags are comma-separated in the CSV
        "blueprint_id": 1098,  # Replace with the actual blueprint ID
        "print_provider_id": 228,
        "variants": [
            {
                "id": 82064,  # Replace with the actual variant ID
                "price": 3999,
                "is_enabled": True
            }
        ],
        "print_areas": [
            {
                "variant_ids": [82064],  # Replace with the actual variant ID
                "placeholders": [
                    {
                        "position": "front",
                        "images": [
                            {
                                "id": image_id,
                                "x": 0.5,
                                "y": 0.5,
                                "scale": 1.0,
                                "angle": 0
                            }
                        ]
                    }
                ]
            }
        ]
    }
    response = requests.post(product_url, headers=headers, json=data)
    if response.status_code >= 200 and response.status_code < 300:
        print(f"Product {idx+1} created successfully!")
    else:
        print(f"Failed to create product {idx+1}. Server responded with: {response.text}")
