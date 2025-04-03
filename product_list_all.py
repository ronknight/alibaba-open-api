import os
import requests
import hashlib
import hmac
import time
from dotenv import load_dotenv
import json
from datetime import datetime
import argparse
from utils.terminal_colors import Colors, print_success, print_error, print_info, print_warning, print_header

# Load environment variables from .env file
load_dotenv()

def generate_signature(params, secret_key, api_operation):
    sorted_params = sorted(params.items())
    concatenated_string = api_operation
    for k, v in sorted_params:
        concatenated_string += f"{k}{v}"
    hashed = hmac.new(secret_key.encode('utf-8'), concatenated_string.encode('utf-8'), hashlib.sha256).hexdigest().upper()
    return hashed

def fetch_products(params, headers, api_operation, server_url, app_secret):
    # Generate the signature
    signature = generate_signature(params, app_secret, api_operation)
    params['sign'] = signature

    try:
        response = requests.post(f"{server_url}{api_operation}", data=params, headers=headers)
        return response.json()
    except requests.exceptions.RequestException as e:
        print_error(f"\nRequest error: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Fetch ALL products from Alibaba API with pagination')
    parser.add_argument('--subject', type=str, help='Subject of product')
    parser.add_argument('--gmt_modified_from', type=str, help='Modified from date')
    parser.add_argument('--gmt_modified_to', type=str, help='Modified to date')
    parser.add_argument('--group_id1', type=int, help='Group ID 1')
    parser.add_argument('--group_id2', type=int, help='Group ID 2')
    parser.add_argument('--group_id3', type=int, help='Group ID 3')
    parser.add_argument('--category_id', type=int, help='Category ID')
    
    args = parser.parse_args()

    # Retrieve parameters from environment
    APP_KEY = os.getenv('APP_KEY')
    APP_SECRET = os.getenv('APP_SECRET')
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    ALIBABA_SERVER_CALL_ENTRY = "https://openapi-api.alibaba.com/rest"
    API_OPERATION = "/alibaba/icbu/product/list"

    # Define the headers
    headers = {
        'X-Protocol': 'GOP',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Prepare logging
    log_dir = 'api_logs'
    os.makedirs(log_dir, exist_ok=True)
    timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")

    # Initialize variables for pagination
    current_page = 1
    page_size = 30
    total_products = []
    
    print_header("\n=== Fetching All Products ===")
    print_info("Page size: 30 products per page")

    while True:
        # Prepare the base request parameters
        params = {
            "app_key": APP_KEY,
            "format": "json",
            "method": API_OPERATION,
            "access_token": ACCESS_TOKEN,
            "sign_method": "sha256",
            "timestamp": str(int(time.time() * 1000)),
            "filter_type": "onSelling",
            "current_page": str(current_page),
            "page_size": str(page_size),
            "schema_custom_fields": "model,4sgm_SKU"  # Request custom fields
        }

        # Add optional parameters if they are provided
        if args.subject:
            params["subject"] = args.subject
        if args.gmt_modified_from:
            params["gmt_modified_from"] = args.gmt_modified_from
        if args.gmt_modified_to:
            params["gmt_modified_to"] = args.gmt_modified_to
        if args.group_id1:
            params["group_id1"] = str(args.group_id1)
        if args.group_id2:
            params["group_id2"] = str(args.group_id2)
        if args.group_id3:
            params["group_id3"] = str(args.group_id3)
        if args.category_id:
            params["category_id"] = str(args.category_id)

        print_info(f"\nFetching page {current_page}...")
        
        # Make the API call
        response_data = fetch_products(params, headers, API_OPERATION, ALIBABA_SERVER_CALL_ENTRY, APP_SECRET)
        
        if not response_data or 'result' not in response_data:
            print_error("Failed to fetch products")
            break

        # Extract products from the response
        if 'products' in response_data['result']:
            page_products = response_data['result']['products']
            total_products.extend(page_products)
            print_success(f"Retrieved {len(page_products)} products from page {current_page}")
            
            # Display total progress with correct key 'total_item'
            total_count = response_data['result']['total_item']
            progress = (len(total_products) / total_count) * 100
            print_info(f"Progress: {len(total_products)}/{total_count} products ({progress:.1f}%)")
            
            # Check if we've reached the end
            if len(total_products) >= total_count:
                print_success(f"\nCompleted! Retrieved all {len(total_products)} products")
                break
        else:
            # Only break if we're on page 4 and no products found
            if current_page == 4:
                print_warning("No products found on page 4, stopping...")
                break
            print_warning("No products found on this page, continuing...")

        current_page += 1
        
        # Only sleep after page 3
        if current_page > 3:
            print_info("Waiting 15 seconds before next request...")
            time.sleep(15)

        # Save to a JSON file
        output_file = os.path.join(log_dir, f"all_products_{timestamp_str}.json")
        with open(output_file, 'w') as f:
            json.dump({
                "total_products": len(total_products),
                "products": total_products,
                "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "query_parameters": {k: v for k, v in params.items() if k not in ['app_key', 'access_token', 'sign']}
            }, f, indent=4)
        
        print_success(f"Products saved to {output_file}")

if __name__ == "__main__":
    main()