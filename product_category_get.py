import os
import requests
import hashlib
import hmac
import time
from dotenv import load_dotenv
import json
from datetime import datetime
import argparse  # Add this import

# Load environment variables from .env file
load_dotenv()

# Function to generate the signature with SHA-256
def generate_signature(params, secret_key, api_operation):
    # Step 1: Sort all request parameters
    sorted_params = sorted(params.items())

    # Step 2: Concatenate the sorted parameters and their values into a string
    concatenated_string = api_operation
    for k, v in sorted_params:
        concatenated_string += f"{k}{v}"

    # Step 3: Generate HMAC SHA-256
    hashed = hmac.new(secret_key.encode('utf-8'), concatenated_string.encode('utf-8'), hashlib.sha256).hexdigest().upper()

    return hashed

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Get product category information from Alibaba API')
    parser.add_argument('category_id', help='The category ID to query')
    args = parser.parse_args()

    # Retrieve parameters from environment
    APP_KEY = os.getenv('APP_KEY')
    APP_SECRET = os.getenv('APP_SECRET')
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    ALIBABA_SERVER_CALL_ENTRY = "https://openapi-api.alibaba.com/rest"
    API_OPERATION = "/icbu/product/category/get"  # Updated to correct path format

    # Prepare the request parameters
    timestamp = str(int(time.time() * 1000))  # Current timestamp in milliseconds
    params = {
        "app_key": APP_KEY,
        "format": "json",
        "method": API_OPERATION,
        "access_token": ACCESS_TOKEN,
        "sign_method": "sha256",
        "timestamp": timestamp,
        "cat_id": args.category_id  # Use the command-line argument here
    }

    # Generate the signature
    signature = generate_signature(params, APP_SECRET, API_OPERATION)

    # Add the generated signature to the params dictionary
    params['sign'] = signature

    # Define the headers
    headers = {
        'X-Protocol': 'GOP',  # Use Protocol.GOP
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Prepare logging
    log_dir = 'api_logs'
    os.makedirs(log_dir, exist_ok=True)
    timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
    log_file_path = os.path.join(log_dir, f"api_request_response_{timestamp_str}.json")

    # Prepare request log (excluding sensitive info)
    request_log = {
        "Request Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Request URL": f"{ALIBABA_SERVER_CALL_ENTRY}",
        "Request Method": "POST",
        "Request Headers": headers,
        "Request Parameters": {
            "format": params.get("format"),
            "method": params.get("method"),
            "timestamp": params.get("timestamp"),
            "sign_method": params.get("sign_method"),
            "cat_id": params.get("cat_id")
        }
    }

    try:
        # Make the POST request - updated to append API operation to base URL
        response = requests.post(f"{ALIBABA_SERVER_CALL_ENTRY}{API_OPERATION}", data=params, headers=headers)
        
        # Handle the response
        response_data = response.json()

        # Prepare response log
        response_log = {
            "Response Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Response Status Code": response.status_code,
            "Response Headers": {
                key: value for key, value in response.headers.items() if key.lower() not in ['authorization', 'set-cookie']
            },
            "Response Body": response_data  # Include the full response body
        }

        # Write logs to file
        with open(log_file_path, 'w') as log_file:
            log_data = {
                "Source": "category_get.py",
                "Request Log": request_log,
                "Response Log": response_log
            }
            json.dump(log_data, log_file, indent=4)
        
        print(f"\nRequest and Response logged to {log_file_path}")

    except requests.exceptions.RequestException as e:
        print(f"\nRequest error: {e}")

if __name__ == "__main__":
    main()