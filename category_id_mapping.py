import os
import requests
import hashlib
import hmac
import time
from dotenv import load_dotenv
import json
from datetime import datetime
from typing import Optional

# Load environment variables from .env file
load_dotenv()

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

def get_category_mapping(
    convert_type: Optional[int] = None,
    cat_id: Optional[int] = None,
    attribute_id: Optional[int] = None,
    attribute_value_id: Optional[int] = None
):
    """
    Get category ID mapping based on provided parameters.
    
    Args:
        convert_type (int, optional): 1-category, 2-attribute, 3-value
        cat_id (int, optional): Category ID
        attribute_id (int, optional): Attribute ID
        attribute_value_id (int, optional): Attribute value ID
    """
    # Retrieve parameters from environment
    APP_KEY = os.getenv('APP_KEY')
    APP_SECRET = os.getenv('APP_SECRET')
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    ALIBABA_SERVER_CALL_ENTRY = "https://openapi-api.alibaba.com/rest"
    API_OPERATION = "/alibaba/icbu/category/id/mapping"

    # Prepare the request parameters
    timestamp = str(int(time.time() * 1000))
    params = {
        "app_key": APP_KEY,
        "format": "json",
        "method": API_OPERATION,
        "access_token": ACCESS_TOKEN,
        "sign_method": "sha256",
        "timestamp": timestamp,
    }

    # Add optional parameters if they are provided
    if convert_type is not None:
        params["convert_type"] = str(convert_type)
    if cat_id is not None:
        params["cat_id"] = str(cat_id)
    if attribute_id is not None:
        params["attribute_id"] = str(attribute_id)
    if attribute_value_id is not None:
        params["attribute_value_id"] = str(attribute_value_id)

    # Generate the signature
    signature = generate_signature(params, APP_SECRET, API_OPERATION)
    params['sign'] = signature

    # Define the headers
    headers = {
        'X-Protocol': 'GOP',
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
        "Request Parameters": {k: v for k, v in params.items() if k not in ['app_key', 'access_token', 'sign']}
    }

    try:
        # Make the POST request
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
            "Response Body": response_data
        }

        # Write logs to file
        with open(log_file_path, 'w') as log_file:
            log_data = {
                "Source": "category_id_mapping.py",
                "Request Log": request_log,
                "Response Log": response_log
            }
            json.dump(log_data, log_file, indent=4)
        
        print(f"\nRequest and Response logged to {log_file_path}")
        return response_data

    except requests.exceptions.RequestException as e:
        print(f"\nRequest error: {e}")
        return None

def main():
    # Example usage
    response = get_category_mapping(
        convert_type=1,  # 1 for category mapping
        cat_id=123456    # Replace with actual category ID
    )
    
    if response and response.get("result", {}).get("success"):
        print("Mapping successful!")
        print(json.dumps(response, indent=2))
    else:
        print("Mapping failed!")
        print(json.dumps(response, indent=2))

if __name__ == "__main__":
    main()