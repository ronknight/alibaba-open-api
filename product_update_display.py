import os
import requests
import hashlib
import hmac
import time
from dotenv import load_dotenv
import json
from datetime import datetime
import argparse
from utils.terminal_colors import print_success, print_error, print_info, print_warning, print_header

# Load environment variables from .env file
load_dotenv()

def generate_signature(params, secret_key, api_operation):
    sorted_params = sorted(params.items())
    concatenated_string = api_operation
    for k, v in sorted_params:
        # Convert all values to strings if they aren't already
        if not isinstance(v, str):
            v = str(v)
        concatenated_string += f"{k}{v}"
    hashed = hmac.new(secret_key.encode('utf-8'), concatenated_string.encode('utf-8'), hashlib.sha256).hexdigest().upper()
    return hashed

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        return obj

def main():
    parser = argparse.ArgumentParser(description='Update product display status (on/off)')
    parser.add_argument('--product_id', type=str, required=True, nargs='+', help='ID(s) of the product(s) to update. Can provide multiple IDs separated by spaces')
    parser.add_argument('--status', type=str, required=True, choices=['on', 'off'], 
                      help='Display status: on (put product on sale) or off (take product off sale)')
    args = parser.parse_args()

    # Clean up product IDs (remove any commas and whitespace)
    product_ids = [id.strip().replace(',', '') for id in args.product_id]

    APP_KEY = os.getenv('APP_KEY')
    APP_SECRET = os.getenv('APP_SECRET')
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    ALIBABA_SERVER_CALL_ENTRY = "https://openapi-api.alibaba.com/rest"
    API_OPERATION = "/icbu/product/update/display"
    
    # Prepare API parameters
    timestamp = str(int(time.time() * 1000))
    
    # Build request string manually to ensure exact format
    request_str = '{' + \
        f'"product_id_list":{json.dumps(product_ids, cls=CustomEncoder)},' + \
        f'"new_display":"{args.status}"' + \
    '}'
    
    params = {
        "app_key": APP_KEY,
        "format": "json",
        "method": API_OPERATION,
        "access_token": ACCESS_TOKEN,
        "sign_method": "sha256",
        "timestamp": timestamp,
        "request": request_str
    }

    # Generate signature
    signature = generate_signature(params, APP_SECRET, API_OPERATION)
    params['sign'] = signature

    headers = {
        'X-Protocol': 'GOP',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
        print_info("\nSending request to Alibaba API...")
        print_info(f"Updating product {args.product_id} display status to: {args.status}")

        # Use urlencode to properly format parameters
        response = requests.post(ALIBABA_SERVER_CALL_ENTRY, data=params, headers=headers)
        response_data = response.json()

        # Display summary of the response
        if response.status_code == 200:
            print_success(f"\nAPI call successful (Status: {response.status_code})")
            if response_data.get('success', False):
                print_success(f"Product {args.product_id} display status updated to {args.status}")
                if 'result' in response_data:
                    result = response_data['result']
                    print_info(f"Modified Time: {result.get('gmtModified')}")
            else:
                print_error("Update failed")
                if 'errorMessage' in response_data:
                    print_error(f"Error message: {response_data['errorMessage']}")
        else:
            print_error(f"\nAPI call failed (Status: {response.status_code})")
            if 'message' in response_data:
                print_error(f"Error message: {response_data['message']}")

    except requests.exceptions.RequestException as e:
        print_error(f"\nRequest error: {e}")

if __name__ == "__main__":
    main()
