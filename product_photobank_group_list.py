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
        concatenated_string += f"{k}{v}"
    hashed = hmac.new(secret_key.encode('utf-8'), concatenated_string.encode('utf-8'), hashlib.sha256).hexdigest().upper()
    return hashed

def main():
    parser = argparse.ArgumentParser(description='List photo bank groups from Alibaba API')
    parser.add_argument('--current_page', type=int, help='Current page number (default: 1)', default=1)
    parser.add_argument('--page_size', type=int, help='Number of records per page (default: 20)', default=20)
    parser.add_argument('--gmt_create_start', type=str, help='Start time of group creation (format: yyyy-MM-dd HH:mm:ss)')
    parser.add_argument('--gmt_create_end', type=str, help='End time of group creation (format: yyyy-MM-dd HH:mm:ss)')
    parser.add_argument('--gmt_modified_start', type=str, help='Start time of group modification (format: yyyy-MM-dd HH:mm:ss)')
    parser.add_argument('--gmt_modified_end', type=str, help='End time of group modification (format: yyyy-MM-dd HH:mm:ss)')
    args = parser.parse_args()

    APP_KEY = os.getenv('APP_KEY')
    APP_SECRET = os.getenv('APP_SECRET')
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    ALIBABA_SERVER_CALL_ENTRY = "https://openapi-api.alibaba.com/rest"
    API_OPERATION = "/icbu/product/photobank/group/list"

    # Create request object
    request_obj = {
        "currentPage": args.current_page,
        "pageSize": args.page_size
    }

    # Add optional date parameters if provided
    if args.gmt_create_start:
        request_obj["gmtCreateStart"] = args.gmt_create_start
    if args.gmt_create_end:
        request_obj["gmtCreateEnd"] = args.gmt_create_end
    if args.gmt_modified_start:
        request_obj["gmtModifiedStart"] = args.gmt_modified_start
    if args.gmt_modified_end:
        request_obj["gmtModifiedEnd"] = args.gmt_modified_end

    # Prepare API parameters
    timestamp = str(int(time.time() * 1000))
    params = {
        "app_key": APP_KEY,
        "format": "json",
        "method": API_OPERATION,
        "access_token": ACCESS_TOKEN,
        "sign_method": "sha256",
        "timestamp": timestamp,
        "request": json.dumps(request_obj)
    }

    # Generate signature
    signature = generate_signature(params, APP_SECRET, API_OPERATION)
    params['sign'] = signature

    headers = {
        'X-Protocol': 'GOP',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Prepare logging
    log_dir = 'api_logs'
    os.makedirs(log_dir, exist_ok=True)
    timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
    log_file_path = os.path.join(log_dir, f"photobank_group_list_{timestamp_str}.json")

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
        print_info("\nSending request to Alibaba API...")
        response = requests.post(ALIBABA_SERVER_CALL_ENTRY, data=params, headers=headers)
        response_data = response.json()

        # Display summary of the response
        if response.status_code == 200:
            print_success(f"\nAPI call successful (Status: {response.status_code})")
            if 'result' in response_data:
                result = response_data['result']
                total = result.get('total', 0)
                groups = result.get('groups', [])
                print_info(f"Total groups: {total}")
                print_info(f"Groups in current page: {len(groups)}")
                
                # Print group details
                if groups:
                    print_header("\nGroup Details:")
                    for group in groups:
                        print_info(f"\nGroup ID: {group.get('groupId')}")
                        print_info(f"Group Name: {group.get('groupName')}")
                        print_info(f"Image Count: {group.get('imageCount', 0)}")
                        print_info(f"Created: {group.get('gmtCreate')}")
                        print_info(f"Modified: {group.get('gmtModified')}")
        else:
            print_error(f"\nAPI call failed (Status: {response.status_code})")
            if 'message' in response_data:
                print_error(f"Error message: {response_data['message']}")

        response_log = {
            "Response Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Response Status Code": response.status_code,
            "Response Headers": {
                key: value for key, value in response.headers.items() 
                if key.lower() not in ['authorization', 'set-cookie']
            },
            "Response Body": response_data
        }

        with open(log_file_path, 'w') as log_file:
            log_data = {
                "Source": "product_photobank_group_list.py",
                "Request Log": request_log,
                "Response Log": response_log
            }
            json.dump(log_data, log_file, indent=4)
        
        print_success(f"\nRequest and Response logged to {log_file_path}")

    except requests.exceptions.RequestException as e:
        print_error(f"\nRequest error: {e}")

if __name__ == "__main__":
    main()
