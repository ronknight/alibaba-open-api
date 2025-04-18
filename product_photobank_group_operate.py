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
    parser = argparse.ArgumentParser(description='Operate on photo bank groups (create/update/delete)')
    parser.add_argument('--operation', type=str, required=True, choices=['create', 'update', 'delete'],
                      help='Operation to perform on the group')
    parser.add_argument('--group_name', type=str, help='Name of the group (required for create/update)')
    parser.add_argument('--group_id', type=str, help='ID of the group (required for update/delete)')
    parser.add_argument('--description', type=str, help='Description of the group (optional for create/update)')
    args = parser.parse_args()

    # Validate arguments based on operation
    if args.operation in ['create', 'update'] and not args.group_name:
        print_error("group_name is required for create and update operations")
        return

    if args.operation in ['update', 'delete'] and not args.group_id:
        print_error("group_id is required for update and delete operations")
        return

    APP_KEY = os.getenv('APP_KEY')
    APP_SECRET = os.getenv('APP_SECRET')
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    ALIBABA_SERVER_CALL_ENTRY = "https://openapi-api.alibaba.com/rest"
    API_OPERATION = "/icbu/product/photobank/group/operate"

    # Create request object based on operation
    request_obj = {
        "operation": args.operation
    }

    if args.operation == 'create':
        request_obj.update({
            "groupName": args.group_name,
            "description": args.description if args.description else ""
        })
    elif args.operation == 'update':
        request_obj.update({
            "groupId": args.group_id,
            "groupName": args.group_name,
            "description": args.description if args.description else ""
        })
    else:  # delete
        request_obj.update({
            "groupId": args.group_id
        })

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
    log_file_path = os.path.join(log_dir, f"photobank_group_operate_{timestamp_str}.json")

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
        print_info(f"\nSending {args.operation} request to Alibaba API...")
        if args.operation == 'create':
            print_info(f"Creating group: {args.group_name}")
        elif args.operation == 'update':
            print_info(f"Updating group {args.group_id}: {args.group_name}")
        else:
            print_info(f"Deleting group: {args.group_id}")

        response = requests.post(ALIBABA_SERVER_CALL_ENTRY, data=params, headers=headers)
        response_data = response.json()

        # Display summary of the response
        if response.status_code == 200:
            print_success(f"\nAPI call successful (Status: {response.status_code})")
            if response_data.get('result', {}).get('success'):
                operation_msg = {
                    'create': f"Group '{args.group_name}' created successfully",
                    'update': f"Group {args.group_id} updated successfully",
                    'delete': f"Group {args.group_id} deleted successfully"
                }
                print_success(operation_msg[args.operation])
                
                # Print additional details for create/update operations
                if args.operation in ['create', 'update']:
                    print_info(f"Group Name: {args.group_name}")
                    if args.description:
                        print_info(f"Description: {args.description}")
            else:
                print_error("Operation failed")
                if 'message' in response_data:
                    print_error(f"Error message: {response_data['message']}")
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
                "Source": "product_photobank_group_operate.py",
                "Request Log": request_log,
                "Response Log": response_log
            }
            json.dump(log_data, log_file, indent=4)
        
        print_success(f"\nRequest and Response logged to {log_file_path}")

    except requests.exceptions.RequestException as e:
        print_error(f"\nRequest error: {e}")

if __name__ == "__main__":
    main()
