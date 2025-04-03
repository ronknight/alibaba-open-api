import os
import requests
import hashlib
import hmac
import time
from datetime import datetime
from dotenv import load_dotenv
import json
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

def fetch_product_details(product_id, app_key, app_secret, access_token):
    ALIBABA_SERVER_CALL_ENTRY = "https://openapi-api.alibaba.com/rest"
    API_OPERATION = "/icbu/product/get"

    # Define the headers
    headers = {
        'X-Protocol': 'GOP',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Create the product_get_request object
    product_get_request = {
        "productId": int(product_id)
    }

    # Prepare the base request parameters
    params = {
        "app_key": app_key,
        "access_token": access_token,
        "sign_method": "sha256",
        "timestamp": str(int(time.time() * 1000)),
        "format": "json",
        "method": "/icbu/product/get",
        "product_get_request": json.dumps(product_get_request)
    }

    # Generate the signature
    signature = generate_signature(params, app_secret, API_OPERATION)
    params['sign'] = signature

    try:
        url = f"{ALIBABA_SERVER_CALL_ENTRY}"
        print_info(f"Making API request to: {url}")
        print_info(f"With product ID: {product_id}")
        
        response = requests.post(url, data=params, headers=headers)
        print_info(f"Response status code: {response.status_code}")
        print_info(f"Response headers: {response.headers}")
        
        try:
            response_text = response.text
            print_info(f"Raw response: {response_text[:500]}...")  # Print first 500 chars of response
        except Exception as e:
            print_error(f"Could not read response text: {e}")
            
        response_data = response.json()
        if response.status_code != 200:
            print_error(f"API Error: Status code {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
            
        if 'error_message' in response_data or 'message' in response_data:
            error_msg = response_data.get('error_message') or response_data.get('message')
            error_code = response_data.get('error_code') or response_data.get('code')
            print_error(f"\nAPI Error: {error_msg}")
            if error_code:
                print_error(f"Error Code: {error_code}")
            return None
            
        return response_data
        
    except requests.exceptions.RequestException as e:
        print_error(f"\nRequest error: {e}")
        return None
    except json.JSONDecodeError as e:
        print_error(f"\nFailed to parse API response: {e}")
        print_error(f"Raw response: {response.text}")
        return None

def save_response_to_json(response_data, product_id):
    try:
        # Create api_logs directory if it doesn't exist
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api_logs')
        os.makedirs(log_dir, exist_ok=True)

        # Generate timestamp for the filename
        timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
        output_file = os.path.join(log_dir, f"product_response_{product_id}_{timestamp_str}.json")

        # Prepare the data to save
        save_data = {
            "request_info": {
                "product_id": product_id,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "endpoint": "/icbu/product/get"
            },
            "response": response_data
        }

        # Save to JSON file with proper formatting
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=4, ensure_ascii=False)

        print_success(f"Response data saved to: {output_file}")
        return output_file
    except Exception as e:
        print_error(f"Error saving response to JSON: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Fetch product details by ID from Alibaba API')
    parser.add_argument('--product_id', type=str, required=True, help='Product ID to fetch details for')
    args = parser.parse_args()

    # Retrieve and validate environment variables
    APP_KEY = os.getenv('APP_KEY')
    APP_SECRET = os.getenv('APP_SECRET')
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

    if not all([APP_KEY, APP_SECRET, ACCESS_TOKEN]):
        print_error("\nMissing required environment variables. Please check your .env file.")
        print_info("Required variables: APP_KEY, APP_SECRET, ACCESS_TOKEN")
        return

    print_header("\n=== Fetching Product Details ===")
    print_info(f"Product ID: {args.product_id}")

    # Make the API call
    response_data = fetch_product_details(args.product_id, APP_KEY, APP_SECRET, ACCESS_TOKEN)

    if response_data:
        print_success("Successfully retrieved product details")
        
        # Save the response to JSON file
        output_file = save_response_to_json(response_data, args.product_id)
        
        if output_file:
            print_success(f"Response data has been saved to {output_file}")
        else:
            print_error("Failed to save response data")
    else:
        print_error("Failed to fetch product details")
        print_info("Please check the product ID and try again")

if __name__ == "__main__":
    main()