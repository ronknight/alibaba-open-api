import os
import requests
import hashlib
import hmac
import time
from datetime import datetime
from dotenv import load_dotenv
import json
import argparse
from utils.terminal_colors import print_success, print_error, print_info, print_warning, print_header

# Load environment variables from .env file
load_dotenv()

def generate_signature(params, secret_key, api_operation):
    sorted_params = sorted(params.items())
    concatenated_string = api_operation
    for k, v in sorted_params:
        concatenated_string += f"{k}{v}"
    hashed = hmac.new(secret_key.encode('utf-8'), concatenated_string.encode('utf-8'), hashlib.sha256).hexdigest().upper()
    return hashed

def update_product_inventory(app_key, app_secret, access_token, product_id, sku_id, quantity, multiple=False):
    ALIBABA_SERVER_CALL_ENTRY = "https://openapi-api.alibaba.com/rest"
    API_OPERATION = "/icbu/product/inventory/update"

    # Define the headers
    headers = {
        'X-Protocol': 'GOP',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Create inventory update request object
    inventory_item = {
        "productId": str(product_id),
        "skuId": str(sku_id),
        "inventory": {
            "amount": str(quantity)
        }
    }

    # If multiple is True, use amountDiff for relative change
    if multiple:
        inventory_item["inventory"]["amountDiff"] = str(quantity)
        del inventory_item["inventory"]["amount"]

    inventory_update_request = {
        "inventoryItems": [inventory_item]
    }

    # Prepare API parameters
    timestamp = str(int(time.time() * 1000))
    params = {
        "app_key": app_key,
        "format": "json",
        "method": API_OPERATION,
        "access_token": access_token,
        "sign_method": "sha256",
        "timestamp": timestamp,
        "inventory_update_request": json.dumps(inventory_update_request)
    }

    # Generate signature
    signature = generate_signature(params, app_secret, API_OPERATION)
    params['sign'] = signature

    try:
        print_info("\nSending request to Alibaba API...")
        print_info(f"Updating inventory for Product ID: {product_id}, SKU ID: {sku_id}")
        if multiple:
            print_info(f"Adjusting quantity by: {quantity}")
        else:
            print_info(f"Setting quantity to: {quantity}")

        response = requests.post(ALIBABA_SERVER_CALL_ENTRY, data=params, headers=headers)
        print_info(f"Response status code: {response.status_code}")

        # Prepare logging
        log_dir = 'api_logs'
        os.makedirs(log_dir, exist_ok=True)
        timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
        log_file_path = os.path.join(log_dir, f"inventory_update_{product_id}_{timestamp_str}.json")

        request_log = {
            "Request Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Request URL": ALIBABA_SERVER_CALL_ENTRY,
            "Request Method": "POST",
            "Request Headers": headers,
            "Request Parameters": {
                key: value for key, value in params.items() 
                if key not in ['app_key', 'access_token', 'sign']
            }
        }

        try:
            response_data = response.json()

            response_log = {
                "Response Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Response Status Code": response.status_code,
                "Response Headers": {
                    key: value for key, value in response.headers.items() 
                    if key.lower() not in ['authorization', 'set-cookie']
                },
                "Response Body": response_data
            }

            # Save logs
            with open(log_file_path, 'w') as log_file:
                log_data = {
                    "Source": "product_inventory_update.py",
                    "Request Log": request_log,
                    "Response Log": response_log
                }
                json.dump(log_data, log_file, indent=4)

            # Handle response
            if response.status_code == 200:
                if response_data.get('success', False):
                    print_success("\nInventory updated successfully")
                    if 'result' in response_data:
                        result = response_data['result']
                        if result.get('success', False):
                            print_success("Update confirmed by API")
                        else:
                            print_warning(f"API Warning: {result.get('message', 'No message provided')}")
                    print_success(f"Response logged to {log_file_path}")
                    return True
                else:
                    error_msg = response_data.get('message', 'Unknown error')
                    print_error(f"\nFailed to update inventory: {error_msg}")
            else:
                print_error(f"\nAPI call failed (Status: {response.status_code})")
                if 'message' in response_data:
                    print_error(f"Error message: {response_data['message']}")

            return False

        except json.JSONDecodeError as e:
            print_error(f"\nFailed to parse API response: {e}")
            print_error(f"Raw response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print_error(f"\nRequest error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Update product inventory quantity')
    parser.add_argument('--product_id', type=str, required=True, help='Product ID to update')
    parser.add_argument('--sku_id', type=str, required=True, help='SKU ID to update')
    parser.add_argument('--quantity', type=int, required=True, help='Quantity to set or adjust')
    parser.add_argument('--adjust', action='store_true', help='Adjust quantity relatively (add/subtract) instead of setting absolute value')
    args = parser.parse_args()

    # Retrieve and validate environment variables
    APP_KEY = os.getenv('APP_KEY')
    APP_SECRET = os.getenv('APP_SECRET')
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

    if not all([APP_KEY, APP_SECRET, ACCESS_TOKEN]):
        print_error("\nMissing required environment variables. Please check your .env file.")
        print_info("Required variables: APP_KEY, APP_SECRET, ACCESS_TOKEN")
        return

    print_header("\n=== Updating Product Inventory ===")
    print_info(f"Product ID: {args.product_id}")
    print_info(f"SKU ID: {args.sku_id}")
    if args.adjust:
        print_info(f"Adjusting quantity by: {args.quantity}")
    else:
        print_info(f"Setting quantity to: {args.quantity}")

    # Make the API call
    update_product_inventory(APP_KEY, APP_SECRET, ACCESS_TOKEN, args.product_id, args.sku_id, args.quantity, args.adjust)

if __name__ == "__main__":
    main()
