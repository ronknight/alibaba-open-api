import os
import requests
import hashlib
import hmac
import time
from dotenv import load_dotenv
import json
from datetime import datetime
import argparse
import re
from utils.terminal_colors import print_success, print_error, print_info, print_warning, print_header

# Load environment variables from .env file
load_dotenv()

def generate_signature(params, secret_key, api_operation):
    """
    Generate the signature for Alibaba API requests
    
    Args:
        params (dict): Parameters to sign
        secret_key (str): API secret key
        api_operation (str): API operation path
    
    Returns:
        str: The generated signature
    """
    sorted_params = sorted(params.items())
    concatenated_string = api_operation
    for k, v in sorted_params:
        # Convert all values to strings if they aren't already
        if not isinstance(v, str):
            v = str(v)
        concatenated_string += f"{k}{v}"
    hashed = hmac.new(secret_key.encode('utf-8'), concatenated_string.encode('utf-8'), hashlib.sha256).hexdigest().upper()
    return hashed

def update_product_display(app_key, app_secret, access_token, product_id, display_status):
    """
    Update product display status (online/offline) using Alibaba API
    
    Args:
        app_key (str): Alibaba API app key
        app_secret (str): Alibaba API app secret
        access_token (str): Alibaba API access token
        product_id (str): The ID of the product to update
        display_status (str): The display status to set ('online' or 'offline')
    
    Returns:
        bool: True if update succeeded, False otherwise
    """
    ALIBABA_SERVER_CALL_ENTRY = "https://openapi-api.alibaba.com/rest"
    API_OPERATION = "/icbu/product/update/display"

    # Define the headers
    headers = {
        'X-Protocol': 'GOP',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    # Convert online/offline to on/off as required by the API
    display_value = "on" if display_status == "online" else "off"    # Prepare API parameters
    timestamp = str(int(time.time() * 1000))
    params = {
        "app_key": app_key,
        "format": "json",
        "method": API_OPERATION,
        "access_token": access_token,
        "sign_method": "sha256",
        "timestamp": timestamp,        "product_id_list": json.dumps([product_id]),
        "new_display": display_value
    }
    
    # Generate signature
    signature = generate_signature(params, app_secret, API_OPERATION)
    params['sign'] = signature

    try:
        print_info("\nSending request to Alibaba API...")
        print_info(f"Updating product {product_id} display status to: {display_status}")
        print_info(f"API parameter value: {display_value}")
        
        # Debug info without sensitive data
        debug_params = {
            k: (v if k not in ['app_key', 'access_token', 'sign'] else '[REDACTED]') 
            for k, v in params.items()
        }

        response = requests.post(ALIBABA_SERVER_CALL_ENTRY, data=params, headers=headers)
        print_info(f"Response status code: {response.status_code}")

        # Prepare logging
        log_dir = 'api_logs'
        os.makedirs(log_dir, exist_ok=True)
        timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
        log_file_path = os.path.join(log_dir, f"product_display_{product_id}_{timestamp_str}.json")
        
        # Create a safe version of the request for logging (no sensitive data)
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
            
            # Create a safe version of the response for logging
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
                    "Source": "product_update_display.py",
                    "Request Log": request_log,
                    "Response Log": response_log
                }
                json.dump(log_data, log_file, indent=4)
            
            # Handle response
            if response.status_code == 200:
                if response_data.get('success', False):
                    print_success("\nProduct display status updated successfully")
                    
                    # Log updated product information
                    result = response_data.get('result', {})
                    if result:
                        print_success(f"Product status set to: {display_status} ({display_value})")
                        print_info(f"Modified Time: {result.get('gmtModified')}")
                    
                    print_info(f"Response logged to {log_file_path}")
                    return True
                else:
                    print_error("\nFailed to update product display status")
                    result = response_data.get('result', {})
                    
                    # Check for fail_id_map which contains detailed error messages
                    if result and 'fail_id_map' in result:
                        for error_msg, product_ids in result['fail_id_map'].items():
                            print_error(f"Error: {error_msg}")
                            print_error(f"Affected product IDs: {', '.join(map(str, product_ids))}")
                            
                            # Special handling for seller ID mismatch
                            if "seller ID and product seller ID are not match" in error_msg:
                                # Extract seller IDs from error message
                                try:
                                    import re
                                    match = re.search(r'\[actual:(\d+),expect:(\d+)\]', error_msg)
                                    if match:
                                        actual_seller = match.group(1)
                                        expected_seller = match.group(2)
                                        print_error(f"\nAuthentication/Permission Issue:")
                                        print_info(f"Your API credentials are for seller ID: {actual_seller}")
                                        print_info(f"The product belongs to seller ID: {expected_seller}")
                                        print_info("To fix this issue, you need to either:")
                                        print_info("1. Use API credentials that belong to the correct seller account")
                                        print_info("2. Verify you're using the correct product ID")
                                        print_info("3. Request access permissions if you're trying to manage products across multiple seller accounts")
                                except:
                                    pass
                    elif 'errorMessage' in response_data:
                        print_error(f"Error message: {response_data['errorMessage']}")
                    elif 'message' in response_data:
                        print_error(f"Error message: {response_data['message']}")
                    else:
                        print_error("Unknown error occurred. Check the log file for details.")
                        
                    return False
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
    parser = argparse.ArgumentParser(description='Update product display status (online/offline)')
    parser.add_argument('--product_id', type=str, required=True, help='ID of the product to update')
    parser.add_argument('--status', type=str, required=True, choices=['online', 'offline'], 
                      help='Display status: online (for sale) or offline (not for sale)')
    args = parser.parse_args()

    # Retrieve and validate environment variables
    APP_KEY = os.getenv('APP_KEY')
    APP_SECRET = os.getenv('APP_SECRET')
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

    if not all([APP_KEY, APP_SECRET, ACCESS_TOKEN]):
        print_error("\nMissing required environment variables. Please check your .env file.")
        print_info("Required variables: APP_KEY, APP_SECRET, ACCESS_TOKEN")
        return

    print_header("\n=== Updating Product Display Status ===")
    print_info(f"Product ID: {args.product_id}")
    print_info(f"New Status: {args.status}")
    
    # Make the API call
    update_product_display(APP_KEY, APP_SECRET, ACCESS_TOKEN, args.product_id, args.status)

if __name__ == "__main__":
    main()
