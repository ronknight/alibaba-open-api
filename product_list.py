import os
import requests
import hashlib
import hmac
import time
from dotenv import load_dotenv
import json
from datetime import datetime
import argparse

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}{msg}{Colors.ENDC}")

def print_error(msg):
    print(f"{Colors.RED}{msg}{Colors.ENDC}")

def print_info(msg):
    print(f"{Colors.BLUE}{msg}{Colors.ENDC}")

def print_warning(msg):
    print(f"{Colors.YELLOW}{msg}{Colors.ENDC}")

def print_header(msg):
    print(f"{Colors.BOLD}{Colors.CYAN}{msg}{Colors.ENDC}")

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

def display_usage_samples():
    """Display sample usage of the script with various parameters"""
    print_header("\n=== Sample Usage ===")
    print_info("Basic usage:")
    print(f"  python product_list.py")
    
    print_info("\nWith specific page and size:")
    print(f"  python product_list.py --current_page 2 --page_size 30")
    
    print_info("\nSearch for products by subject:")
    print(f"  python product_list.py --subject \"T-shirt\"")
    
    print_info("\nFilter by modification date range:")
    print(f"  python product_list.py --gmt_modified_from \"2023-01-01T00:00:00Z\" --gmt_modified_to \"2023-12-31T23:59:59Z\"")
    
    print_info("\nFilter by category and group:")
    print(f"  python product_list.py --category_id 123456 --group_id1 789")
    
    print_info("\nGet specific product by ID:")
    print(f"  python product_list.py --id 123456789")
    
    print_info("\nWith multiple filters combined:")
    print(f"  python product_list.py --current_page 1 --page_size 20 --subject \"Shoes\" --category_id 12345")
    
    print()

# Example usage of the signature generation function
def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Fetch product list from Alibaba API with colored output')
    parser.add_argument('--current_page', type=int, help='Current page number')
    parser.add_argument('--subject', type=str, help='Subject of product')
    parser.add_argument('--page_size', type=int, help='Page size of the query')
    parser.add_argument('--gmt_modified_from', type=str, help='Modified from date')
    parser.add_argument('--gmt_modified_to', type=str, help='Modified to date')
    parser.add_argument('--group_id1', type=int, help='Group ID 1')
    parser.add_argument('--group_id2', type=int, help='Group ID 2')
    parser.add_argument('--group_id3', type=int, help='Group ID 3')
    parser.add_argument('--id', type=int, help='Product ID')
    parser.add_argument('--category_id', type=int, help='Category ID')
    parser.add_argument('--show_examples', action='store_true', help='Show usage examples and exit')
    
    args = parser.parse_args()
    
    # If --show_examples flag is used, display usage samples and exit
    if args.show_examples:
        display_usage_samples()
        return

    # Retrieve parameters from environment
    APP_KEY = os.getenv('APP_KEY')
    APP_SECRET = os.getenv('APP_SECRET')
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    ALIBABA_SERVER_CALL_ENTRY = "https://openapi-api.alibaba.com/rest"
    API_OPERATION = "/alibaba/icbu/product/list"  # API operation endpoint for GOP protocol

    # Prepare the base request parameters
    params = {
        "app_key": APP_KEY,
        "format": "json",
        "method": API_OPERATION,
        "access_token": ACCESS_TOKEN,
        "sign_method": "sha256",
        "timestamp": str(int(time.time() * 1000)),
        "filter_type": "onSelling"
    }

    # Add optional parameters if they are provided
    if args.current_page:
        params["current_page"] = str(args.current_page)
    else:
        params["current_page"] = "1"  # Default value
        
    if args.page_size:
        params["page_size"] = str(args.page_size)
    else:
        params["page_size"] = "20"  # Default value
        
    if args.subject:
        params["subject"] = args.subject
    if args.gmt_modified_from:
        params["gmt_modified_from"] = args.gmt_modified_from
    if args.gmt_modified_to:
        params["gmt_modified_to"] = args.gmt_modified_to
    if args.group_id1:
        params["group_id1"] = str(args.group_id1)
    if args.group_id2:
        params["group_id2"] = str(args.group_id2)
    if args.group_id3:
        params["group_id3"] = str(args.group_id3)
    if args.id:
        params["id"] = str(args.id)
    if args.category_id:
        params["category_id"] = str(args.category_id)

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
        "Request Parameters": {key: value for key, value in params.items() 
                              if key not in ['app_key', 'access_token', 'sign']}
    }

    # Display the parameters being used
    print_header("\n=== API Call Parameters ===")
    for key, value in params.items():
        if key not in ['app_key', 'access_token', 'sign']:
            print(f"{Colors.YELLOW}{key}{Colors.ENDC}: {value}")
    
    # Display optional parameters information
    print_header("\n=== Available Optional Parameters ===")
    optional_params = {
        "current_page": {
            "description": "Current page number",
            "default": "1"
        },
        "subject": {
            "description": "Subject of product"
        },
        "page_size": {
            "description": "Page size of the query (1-50)",
            "default": "20"
        },
        "gmt_modified_from": {
            "description": "Modified from date (format: YYYY-MM-DDThh:mm:ssZ)"
        },
        "gmt_modified_to": {
            "description": "Modified to date (format: YYYY-MM-DDThh:mm:ssZ)"
        },
        "group_id1": {
            "description": "Group ID 1"
        },
        "group_id2": {
            "description": "Group ID 2"
        },
        "group_id3": {
            "description": "Group ID 3"
        },
        "id": {
            "description": "Product ID"
        },
        "category_id": {
            "description": "Category ID"
        },
        "filter_type": {
            "description": "Status of products to retrieve",
            "options": ["onSelling", "approved", "auditing", "editingRequired", "expired"],
            "default": "onSelling"
        }
    }
    
    print_info("The following optional parameters can be used:")
    for param, details in optional_params.items():
        if param in params:
            param_status = f"(current: {params[param]})"
        else:
            param_status = "(not specified)"
            
        print(f"{Colors.YELLOW}{param}{Colors.ENDC} {param_status} - {details['description']}")
        
        if 'options' in details:
            options_str = ", ".join(details['options'])
            print(f"  Options: {options_str}")
        if 'default' in details:
            print(f"  Default: {details['default']}")
    
    # Display sample usage
    print_info("\nFor usage examples, run:")
    print(f"  python product_list.py --show_examples")
    print()

    try:
        # Make the POST request
        print_info("\nSending request to Alibaba API...")
        response = requests.post(f"{ALIBABA_SERVER_CALL_ENTRY}{API_OPERATION}", data=params, headers=headers)
        
        # Handle the response
        response_data = response.json()
        
        # Display a summary of the response
        if response.status_code == 200:
            print_success(f"\nAPI call successful (Status: {response.status_code})")
            if 'result' in response_data and 'total' in response_data['result']:
                print_info(f"Total products: {response_data['result']['total']}")
                if 'products' in response_data['result']:
                    print_info(f"Products returned: {len(response_data['result']['products'])}")
        else:
            print_error(f"\nAPI call failed (Status: {response.status_code})")
            if 'message' in response_data:
                print_error(f"Error message: {response_data['message']}")

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
                "Source": "productlist.py",
                "Request Log": request_log,
                "Response Log": response_log
            }
            json.dump(log_data, log_file, indent=4)
        
        print_success(f"\nRequest and Response logged to {log_file_path}")

    except requests.exceptions.RequestException as e:
        print_error(f"\nRequest error: {e}")

if __name__ == "__main__":
    main()
