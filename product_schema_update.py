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

def update_product_schema(app_key, app_secret, access_token, schema_id, schema_data):
    ALIBABA_SERVER_CALL_ENTRY = "https://openapi-api.alibaba.com/rest"
    API_OPERATION = "/icbu/product/schema/update"

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
        "schema_id": str(schema_id),
        "schema_data": json.dumps(schema_data)
    }

    # Generate signature
    signature = generate_signature(params, app_secret, API_OPERATION)
    params['sign'] = signature

    try:
        print_info("\nSending request to Alibaba API...")
        print_info(f"Updating schema: {schema_id}")

        response = requests.post(ALIBABA_SERVER_CALL_ENTRY, data=params, headers=headers)
        print_info(f"Response status code: {response.status_code}")

        # Prepare logging
        log_dir = 'api_logs'
        os.makedirs(log_dir, exist_ok=True)
        timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
        log_file_path = os.path.join(log_dir, f"schema_update_{timestamp_str}.json")

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
                    "Source": "product_schema_update.py",
                    "Request Log": request_log,
                    "Response Log": response_log
                }
                json.dump(log_data, log_file, indent=4)

            # Handle response
            if response.status_code == 200:
                if response_data.get('success', False):
                    print_success("\nSchema updated successfully")
                    
                    # Log updated schema information
                    result = response_data.get('result', {})
                    if result:
                        print_info(f"Updated Schema ID: {result.get('schemaId')}")
                        if 'updateTime' in result:
                            print_info(f"Update Time: {result.get('updateTime')}")
                    
                    print_success(f"Response logged to {log_file_path}")
                    return result
                else:
                    error_msg = response_data.get('errorMessage', 'Unknown error')
                    print_error(f"\nFailed to update schema: {error_msg}")
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
    parser = argparse.ArgumentParser(description='Update an existing product schema')
    parser.add_argument('--schema_id', type=str, required=True, help='Schema ID to update')
    parser.add_argument('--schema_file', type=str, required=True, help='Path to JSON file containing updated schema data')
    args = parser.parse_args()

    # Retrieve and validate environment variables
    APP_KEY = os.getenv('APP_KEY')
    APP_SECRET = os.getenv('APP_SECRET')
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

    if not all([APP_KEY, APP_SECRET, ACCESS_TOKEN]):
        print_error("\nMissing required environment variables. Please check your .env file.")
        print_info("Required variables: APP_KEY, APP_SECRET, ACCESS_TOKEN")
        return

    # Load schema data from file
    try:
        with open(args.schema_file, 'r') as f:
            schema_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print_error(f"\nError loading schema file: {e}")
        return

    print_header("\n=== Updating Product Schema ===")
    print_info(f"Schema ID: {args.schema_id}")
    print_info(f"Schema File: {args.schema_file}")

    # Make the API call
    update_product_schema(APP_KEY, APP_SECRET, ACCESS_TOKEN, args.schema_id, schema_data)

if __name__ == "__main__":
    main()
