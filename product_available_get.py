#!/usr/bin/env python3
import os
import json
import time
import argparse
from datetime import datetime
from utils.terminal_colors import print_error, print_info, print_header, print_success

def generate_signature(params, app_secret, api_operation):
    """Generate signature for API request"""
    # Sort parameters by key
    sorted_params = sorted(params.items(), key=lambda x: x[0])
    
    # Create the string to sign
    string_to_sign = api_operation
    for key, value in sorted_params:
        string_to_sign += key + str(value)
    
    # Add app secret at the beginning and end
    string_to_sign = app_secret + string_to_sign + app_secret
    
    # Generate signature using SHA256
    import hashlib
    signature = hashlib.sha256(string_to_sign.encode('utf-8')).hexdigest().upper()
    return signature

def check_product_availability(app_key, app_secret, access_token, product_id):
    ALIBABA_SERVER_CALL_ENTRY = "https://openapi-api.alibaba.com/rest"
    API_OPERATION = "/icbu/product/other/available/get"

    # Define the headers
    headers = {
        'X-Protocol': 'GOP',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Create the product request object
    product_request = {
        "productId": str(product_id)
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
        "product_id": str(product_id)
    }

    # Generate signature
    signature = generate_signature(params, app_secret, API_OPERATION)
    params['sign'] = signature

    try:
        print_info("\nSending request to Alibaba API...")
        
        # Import requests here to avoid global import
        import requests
        
        # Make the API call
        response = requests.post(
            ALIBABA_SERVER_CALL_ENTRY,
            headers=headers,
            data=params
        )
        
        # Prepare logging
        log_dir = 'api_logs'
        os.makedirs(log_dir, exist_ok=True)
        timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
        log_file_path = os.path.join(log_dir, f"api_response_{timestamp_str}.json")

        # Save the API response to a log file
        with open(log_file_path, 'w', encoding='utf-8') as f:
            json.dump(response.json(), f, ensure_ascii=False, indent=2)
            print_info(f"\nAPI response saved to: {log_file_path}")

        # Parse and return the response
        return response.json()

    except Exception as e:
        print_error(f"\nError occurred: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Check product availability on Alibaba')
    parser.add_argument('--product_id', type=str, required=True, help='Product ID to check availability for')
    args = parser.parse_args()

    # Retrieve and validate environment variables
    APP_KEY = os.getenv('APP_KEY')
    APP_SECRET = os.getenv('APP_SECRET')
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

    if not all([APP_KEY, APP_SECRET, ACCESS_TOKEN]):
        print_error("\nMissing required environment variables. Please check your .env file.")
        print_info("Required variables: APP_KEY, APP_SECRET, ACCESS_TOKEN")
        return

    print_header("\n=== Checking Product Availability ===")
    print_info(f"Product ID: {args.product_id}")

    # Make the API call
    result = check_product_availability(APP_KEY, APP_SECRET, ACCESS_TOKEN, args.product_id)
    
    if result:
        if result.get('success', False):
            print_success("\nProduct availability check successful!")
            print_info("\nResponse details:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print_error("\nAPI call failed!")
            print_error(f"Error message: {result.get('message', 'Unknown error')}")
    else:
        print_error("\nFailed to get response from API")

if __name__ == "__main__":
    main()
