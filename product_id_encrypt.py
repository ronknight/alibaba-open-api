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

def encrypt_product_id(app_key, app_secret, access_token, product_id, convert_type):
    ALIBABA_SERVER_CALL_ENTRY = "https://openapi-api.alibaba.com/rest"
    API_OPERATION = "/alibaba/icbu/product/id/encrypt"

    # Define the headers
    headers = {
        'X-Protocol': 'GOP',
        'Content-Type': 'application/x-www-form-urlencoded'
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
        "convert_type": str(convert_type),  # 1: original ID to encrypted ID, 2: encrypted ID to original ID
        "product_id": str(product_id)
    }

    # Generate signature
    signature = generate_signature(params, app_secret, API_OPERATION)
    params['sign'] = signature

    try:
        print_info("\nSending request to Alibaba API...")
        operation_type = "encrypt" if convert_type == "1" else "decrypt"
        print_info(f"{operation_type.capitalize()}ing product ID: {product_id}")

        response = requests.post(ALIBABA_SERVER_CALL_ENTRY, data=params, headers=headers)
        print_info(f"Response status code: {response.status_code}")

        # Prepare logging
        log_dir = 'api_logs'
        os.makedirs(log_dir, exist_ok=True)
        timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
        log_file_path = os.path.join(log_dir, f"product_id_encrypt_{timestamp_str}.json")

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
                    "Source": "product_id_encrypt.py",
                    "Request Log": request_log,
                    "Response Log": response_log
                }
                json.dump(log_data, log_file, indent=4)

            # Handle response
            if response.status_code == 200:
                if response_data.get('result', {}).get('success', False):
                    result = response_data.get('result', {})
                    converted_id = result.get('id')
                    print_success(f"\nSuccessfully {operation_type}ed product ID")
                    print_info(f"Original ID: {product_id}")
                    print_info(f"Converted ID: {converted_id}")
                    print_success(f"Response logged to {log_file_path}")
                    return converted_id
                else:
                    error_msg = response_data.get('result', {}).get('msg', 'Unknown error')
                    print_error(f"\nFailed to {operation_type} product ID: {error_msg}")
            else:
                print_error(f"\nAPI call failed (Status: {response.status_code})")
                if 'message' in response_data:
                    print_error(f"Error message: {response_data['message']}")

            return None

        except json.JSONDecodeError as e:
            print_error(f"\nFailed to parse API response: {e}")
            print_error(f"Raw response: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print_error(f"\nRequest error: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Convert between original and encrypted product IDs')
    parser.add_argument('--product_id', type=str, required=True, help='Product ID to convert')
    parser.add_argument('--convert_type', type=str, choices=['1', '2'], required=True,
                      help='1: Convert original ID to encrypted ID, 2: Convert encrypted ID to original ID')
    args = parser.parse_args()

    # Retrieve and validate environment variables
    APP_KEY = os.getenv('APP_KEY')
    APP_SECRET = os.getenv('APP_SECRET')
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

    if not all([APP_KEY, APP_SECRET, ACCESS_TOKEN]):
        print_error("\nMissing required environment variables. Please check your .env file.")
        print_info("Required variables: APP_KEY, APP_SECRET, ACCESS_TOKEN")
        return

    print_header("\n=== Product ID Conversion ===")
    operation = "Encryption" if args.convert_type == "1" else "Decryption"
    print_info(f"Operation: {operation}")
    print_info(f"Product ID: {args.product_id}")

    # Make the API call
    encrypt_product_id(APP_KEY, APP_SECRET, ACCESS_TOKEN, args.product_id, args.convert_type)

if __name__ == "__main__":
    main()
