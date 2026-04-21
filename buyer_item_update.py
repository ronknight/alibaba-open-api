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

def update_buyer_item(product_id, app_key, app_secret, access_token, description=None, cat_id=None, language="ENGLISH", website=None):
    """
    Update buyer item using /icbu/product/schema/update endpoint via POST
    
    Args:
        product_id (str): Product ID to update
        app_key (str): Alibaba API app key
        app_secret (str): Alibaba API app secret
        access_token (str): Alibaba API access token
        description (str): Product description (optional, reads from sample.json if not provided)
        cat_id (str): Category ID (required for schema update)
        language (str): Language code (default: ENGLISH)
        website (str): Website to process product on (ICBU or ALIEXPRESS)
    
    Returns:
        dict: API response data or None if failed
    """
    ALIBABA_SERVER_CALL_ENTRY = "https://openapi-api.alibaba.com/rest"
    API_OPERATION = "/icbu/product/schema/update"

    # Read description from sample.json if not provided
    if description is None:
        with open('data/sample.json', 'r', encoding='utf-8') as f:
            sample_data = json.load(f)
            description = sample_data['product']['description']
    
    # If cat_id not provided, we need to fetch product details first
    if cat_id is None:
        print_info(f"Fetching product details to get category ID...")
        # For now, cat_id is required - user must provide it
        print_error("cat_id parameter is required for schema update")
        return None

    headers = {
        'X-Protocol': 'GOP',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Create the XML schema data format required by schema/update endpoint
    # Escape special XML characters in description
    escaped_desc = description.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')
    
    schema_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<ProductEdit>
    <Description>{escaped_desc}</Description>
</ProductEdit>"""

    # First create params without signature
    params = {
        "app_key": app_key,
        "access_token": access_token,
        "sign_method": "sha256",
        "timestamp": str(int(time.time() * 1000)),
        "format": "json",
        "method": API_OPERATION,
        "product_id": str(product_id),
        "cat_id": str(cat_id),
        "language": language,
        "xml": schema_xml  # XML data required by schema/update endpoint
    }
    
    # Then generate and add the signature
    signature = generate_signature(params, app_secret, API_OPERATION)
    params['sign'] = signature

    try:
        print_info(f"Making API request to: {ALIBABA_SERVER_CALL_ENTRY}")
        print_info(f"Updating buyer item for product ID: {product_id}")
        print_info(f"API endpoint: {API_OPERATION}")
        
        response = requests.post(ALIBABA_SERVER_CALL_ENTRY, data=params, headers=headers)
        print_info(f"Response status code: {response.status_code}")
        
        if response.status_code != 200:
            print_error(f"API Error: Status code {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
            
        response_data = response.json()
        if 'error_message' in response_data or 'message' in response_data:
            error_msg = response_data.get('error_message') or response_data.get('message')
            error_code = response_data.get('error_code') or response_data.get('code')
            print_error(f"\nAPI Error: {error_msg}")
            if error_code:
                print_error(f"Error Code: {error_code}")
            return None

        print_success("\nBuyer item updated successfully")
        return response_data

    except requests.exceptions.RequestException as e:
        print_error(f"\nRequest error: {e}")
        return None
    except json.JSONDecodeError as e:
        print_error(f"\nFailed to parse API response: {e}")
        print_error(f"Raw response: {response.text}")
        return None

def save_response_to_json(response_data, product_id):
    """Save API response to JSON file"""
    try:
        # Create api_logs directory if it doesn't exist
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api_logs')
        os.makedirs(log_dir, exist_ok=True)

        # Generate timestamp for the filename
        timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
        output_file = os.path.join(log_dir, f"buyer_item_update_{product_id}_{timestamp_str}.json")

        # Prepare the data to save
        save_data = {
            "request_info": {
                "product_id": product_id,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "endpoint": "/icbu/product/schema/update"
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
    parser = argparse.ArgumentParser(description='Update buyer item using /icbu/product/schema/update endpoint')
    parser.add_argument('--product_id', type=str, required=True, help='Product ID to update')
    parser.add_argument('--cat_id', type=str, required=True, help='Category ID (required for schema update)')
    parser.add_argument('--description', type=str, help='Product description (if not provided, reads from data/sample.json)')
    parser.add_argument('--language', type=str, default='ENGLISH', help='Language code (default: ENGLISH)')
    parser.add_argument('--website', type=str, choices=['ICBU', 'ALIEXPRESS'], help='Website to process product on')
    args = parser.parse_args()

    # Retrieve and validate environment variables
    APP_KEY = os.getenv('APP_KEY')
    APP_SECRET = os.getenv('APP_SECRET')
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

    if not all([APP_KEY, APP_SECRET, ACCESS_TOKEN]):
        print_error("\nMissing required environment variables. Please check your .env file.")
        print_info("Required variables: APP_KEY, APP_SECRET, ACCESS_TOKEN")
        return

    print_header("\n=== Updating Buyer Item ===")
    print_info(f"Product ID: {args.product_id}")
    if args.website:
        print_info(f"Website: {args.website}")

    try:
        response_data = update_buyer_item(
            args.product_id, 
            APP_KEY, 
            APP_SECRET, 
            ACCESS_TOKEN, 
            args.description,
            args.cat_id,
            args.language,
            args.website
        )
        
        if response_data:
            # Save the response to JSON file
            output_file = save_response_to_json(response_data, args.product_id)
            
            if output_file:
                print_success(f"Response data has been saved to {output_file}")
            else:
                print_error("Failed to save response data")
        else:
            print_error("Failed to update buyer item")
            print_info("Please check the product ID and try again")
            
    except FileNotFoundError:
        print_error("\nSample file not found: data/sample.json")
    except Exception as e:
        print_error(f"\nError processing request: {str(e)}")

if __name__ == "__main__":
    main()
