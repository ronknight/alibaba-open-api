import os
import requests
import hashlib
import hmac
import time
import mimetypes
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

def get_image_info(image_path):
    """Get image information like size and mime type"""
    file_size = os.path.getsize(image_path)
    mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type:
        mime_type = 'application/octet-stream'
    return file_size, mime_type

def main():
    parser = argparse.ArgumentParser(description='Upload image to Alibaba photo bank')
    parser.add_argument('--file_path', type=str, required=True, help='Path to the image file to upload')
    parser.add_argument('--group_id', type=str, required=True, help='Group ID to upload image to')
    parser.add_argument('--image_name', type=str, help='Name for the uploaded image (optional, defaults to filename)')
    args = parser.parse_args()

    # Validate file exists and is readable
    if not os.path.isfile(args.file_path):
        print_error(f"File not found: {args.file_path}")
        return
    
    if not args.image_name:
        args.image_name = os.path.basename(args.file_path)

    # Get file information
    file_size, mime_type = get_image_info(args.file_path)
    
    APP_KEY = os.getenv('APP_KEY')
    APP_SECRET = os.getenv('APP_SECRET')
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    ALIBABA_SERVER_CALL_ENTRY = "https://openapi-api.alibaba.com/rest"
    API_OPERATION = "/alibaba/icbu/photobank/upload"

    # Create request object
    request_obj = {
        "groupId": args.group_id,
        "imageName": args.image_name
    }

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

    # Prepare file for upload
    files = {
        'file': (args.image_name, open(args.file_path, 'rb'), mime_type)
    }

    headers = {
        'X-Protocol': 'GOP'
    }

    # Prepare logging
    log_dir = 'api_logs'
    os.makedirs(log_dir, exist_ok=True)
    timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
    log_file_path = os.path.join(log_dir, f"photobank_upload_{timestamp_str}.json")

    request_log = {
        "Request Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Request URL": ALIBABA_SERVER_CALL_ENTRY,
        "Request Method": "POST",
        "Request Headers": headers,
        "Request Parameters": {
            key: value for key, value in params.items() 
            if key not in ['app_key', 'access_token', 'sign']
        },
        "File Info": {
            "name": args.image_name,
            "size": file_size,
            "mime_type": mime_type
        }
    }

    try:
        print_info("\nSending request to Alibaba API...")
        print_info(f"Uploading file: {args.image_name}")
        print_info(f"File size: {file_size} bytes")
        print_info(f"Target group: {args.group_id}")

        response = requests.post(
            ALIBABA_SERVER_CALL_ENTRY,
            data=params,
            files=files,
            headers=headers
        )
        
        response_data = response.json()

        # Display summary of the response
        if response.status_code == 200:
            print_success(f"\nAPI call successful (Status: {response.status_code})")
            if response_data.get('success', False):
                print_success("Image uploaded successfully")
                if 'image' in response_data:
                    image_info = response_data['image']
                    print_info(f"Image ID: {image_info.get('imageId')}")
                    print_info(f"Image URL: {image_info.get('imageUrl')}")
                    print_info(f"Image Size: {image_info.get('imageSize')} bytes")
            else:
                print_error("Upload failed")
                if 'errorMessage' in response_data:
                    print_error(f"Error message: {response_data['errorMessage']}")
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
                "Source": "product_photobank_upload.py",
                "Request Log": request_log,
                "Response Log": response_log
            }
            json.dump(log_data, log_file, indent=4)
        
        print_success(f"\nRequest and Response logged to {log_file_path}")

    except requests.exceptions.RequestException as e:
        print_error(f"\nRequest error: {e}")
    finally:
        files['file'][1].close()

if __name__ == "__main__":
    main()
