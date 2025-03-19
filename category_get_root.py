import os
import requests
import hashlib
import hmac
import time
from dotenv import load_dotenv
import json
from datetime import datetime

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
    APP_KEY = os.getenv('APP_KEY')
    APP_SECRET = os.getenv('APP_SECRET')
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    ALIBABA_SERVER_CALL_ENTRY = "https://openapi-api.alibaba.com/rest"
    API_OPERATION = "/icbu/product/category/get"

    timestamp = str(int(time.time() * 1000))
    params = {
        "app_key": APP_KEY,
        "format": "json",
        "method": API_OPERATION,
        "access_token": ACCESS_TOKEN,
        "sign_method": "sha256",
        "timestamp": timestamp,
        "cat_id": "0"  # Root category ID to get all top-level categories
    }

    signature = generate_signature(params, APP_SECRET, API_OPERATION)
    params['sign'] = signature

    headers = {
        'X-Protocol': 'GOP',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    log_dir = 'api_logs'
    os.makedirs(log_dir, exist_ok=True)
    timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
    log_file_path = os.path.join(log_dir, f"api_request_response_{timestamp_str}.json")

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
        response = requests.post(ALIBABA_SERVER_CALL_ENTRY, data=params, headers=headers)
        response_data = response.json()

        response_log = {
            "Response Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Response Status Code": response.status_code,
            "Response Headers": {
                key: value for key, value in response.headers.items() if key.lower() not in ['authorization', 'set-cookie']
            },
            "Response Body": response_data
        }

        with open(log_file_path, 'w') as log_file:
            log_data = {
                "Source": "category_get_root.py",
                "Request Log": request_log,
                "Response Log": response_log
            }
            json.dump(log_data, log_file, indent=4)
        
        print(f"\nRequest and Response logged to {log_file_path}")

        # If successful, print the child categories
        if response_data.get("result", {}).get("result", {}).get("child_ids"):
            print("\nRoot category child IDs:")
            print(response_data["result"]["result"]["child_ids"])

    except requests.exceptions.RequestException as e:
        print(f"\nRequest error: {e}")

if __name__ == "__main__":
    main()