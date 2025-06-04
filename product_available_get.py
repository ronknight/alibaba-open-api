#!/usr/bin/env python3
import os
import json
import time
import argparse
import hmac
import hashlib
from datetime import datetime
from utils.terminal_colors import print_error, print_info, print_header, print_success

def generate_signature(params, secret_key, api_operation):
    sorted_params = sorted(params.items())
    concatenated_string = api_operation
    for k, v in sorted_params:
        concatenated_string += f"{k}{v}"
    hashed = hmac.new(secret_key.encode('utf-8'), concatenated_string.encode('utf-8'), hashlib.sha256).hexdigest().upper()
    return hashed

def check_product_availability(app_key, app_secret, access_token, product_id):
    ALIBABA_SERVER_CALL_ENTRY = "https://openapi-api.alibaba.com/rest"
    API_OPERATION = "/icbu/product/other/available/get"
    
    print_info("\nSending request to Alibaba API...")

    # Define the headers
    headers = {
        'X-Protocol': 'GOP',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    # First, get the product details to get the category ID
    import requests
    get_product_params = {
        "app_key": app_key,
        "access_token": access_token,
        "sign_method": "sha256",
        "timestamp": str(int(time.time() * 1000)),
        "format": "json",
        "method": "/icbu/product/get",
        "product_get_request": json.dumps({"productId": int(product_id)})
    }
    get_product_signature = generate_signature(get_product_params, app_secret, "/icbu/product/get")
    get_product_params['sign'] = get_product_signature
    
    product_response = requests.post(
        ALIBABA_SERVER_CALL_ENTRY,
        headers=headers,
        data=get_product_params
    ).json()
    
    if 'product' not in product_response:
        print_error("Failed to get product details")
        return None
        
    category_id = product_response['product']['categoryId']
    
    # Prepare API parameters for availability check
    timestamp = str(int(time.time() * 1000))
    
    # Prepare API parameters
    params = {
        "app_key": app_key,
        "format": "json",
        "method": API_OPERATION,
        "access_token": access_token,
        "sign_method": "sha256",
        "timestamp": timestamp,
        "product_id": product_id,
        "cat_id": category_id,
        "language": "en"
    }

    # Generate signature
    signature = generate_signature(params, app_secret, API_OPERATION)
    params['sign'] = signature

    try:
        print_info("\nSending request to check availability...")
        
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
        log_file_path = os.path.join(log_dir, f"api_response_{timestamp_str}.json")        # Save the API response to a log file
        with open(log_file_path, 'w', encoding='utf-8') as f:
            json.dump(response.json(), f, ensure_ascii=False, indent=2)
            print_info(f"\nAPI response saved to: {log_file_path}")
            
        # Parse the response
        response_data = response.json()
        
        if 'result' in response_data and response_data.get('code') == '0':
            result = response_data['result']
            if result.get('success'):
                data = result.get('data', {})
                print_success("\nProduct Availability Status:")
                print_info(f"Support Post Wholesale: {data.get('supportPostWholeSale', False)}")
                print_info(f"Support Post Sourcing: {data.get('supportPostSourcing', False)}")
                return data  # Return just the availability data
        
        # Only show error if we didn't return successfully above
        print_error("\nAPI call failed!")
        if 'error_message' in response_data:
            print_error(f"Error message: {response_data['error_message']}")
        elif 'message' in response_data:
            print_error(f"Error message: {response_data['message']}")
        elif not response_data.get('result', {}).get('success', False):
            print_error("Error: API call was not successful")
        else:
            print_error("Error: Unexpected response format")
            
        return None

    except Exception as e:
        print_error(f"\nError occurred: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Check product availability on Alibaba')
    parser.add_argument('--product_id', type=str, required=True, help='Product ID to check availability for')
    args = parser.parse_args()
    
    print_header("=== Checking Product Availability ===")
    print_info(f"Product ID: {args.product_id}")

    # Retrieve and validate environment variables
    APP_KEY = os.getenv('APP_KEY')
    APP_SECRET = os.getenv('APP_SECRET')
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

    if not all([APP_KEY, APP_SECRET, ACCESS_TOKEN]):
        print_error("\nMissing required environment variables. Please check your .env file.")
        print_info("Required variables: APP_KEY, APP_SECRET, ACCESS_TOKEN")
        return

    # Make the API call
    result = check_product_availability(APP_KEY, APP_SECRET, ACCESS_TOKEN, args.product_id)
    
    if result is not None:
        print_success("\nProduct availability check successful!")
        print_info("\nResponse details:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_error("\nFailed to get response from API")

if __name__ == "__main__":
    main()
