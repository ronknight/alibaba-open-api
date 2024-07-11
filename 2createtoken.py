import os
import requests
import hashlib
import time
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve variables from environment
APP_KEY = os.getenv('APP_KEY')
APP_SECRET = os.getenv('APP_SECRET')
AUTH_CODE = os.getenv('AUTH_CODE')

# ALIBABA_SERVER_CALL_ENTRY = "https://openapi-api.alibaba.com/rest"
ALIBABA_SERVER_CALL_ENTRY = "https://openapi-auth.alibaba.com/oauth"

API_OPERATION = "/auth/token/create"
LOG_DIR = 'api_logs/'  # Directory to store log files

# Create directory if it does not exist
os.makedirs(LOG_DIR, exist_ok=True)

# Function to log API request and response
def log_request_response(request_params, response_data, url, log_dir):
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    log_file_path = os.path.join(log_dir, f"createtoken_{timestamp}.log")
    
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"Request URL: {url}\n")
        log_file.write("Request Parameters:\n")
        log_file.write(json.dumps(request_params, indent=4) + "\n\n")
        log_file.write("Response Data:\n")
        log_file.write(json.dumps(response_data, indent=4) + "\n")
    
    print(f"API request and response logged in {log_file_path}")

# Function to update the .env file
def update_env_file(key, value, env_file_path='.env'):
    with open(env_file_path, 'r') as file:
        lines = file.readlines()
    
    key_found = False
    with open(env_file_path, 'w') as file:
        for line in lines:
            if line.startswith(f"{key}="):
                file.write(f"{key}={value}\n")
                key_found = True
            else:
                file.write(line)
        
        if not key_found:
            file.write(f"{key}={value}\n")
    
    print(f"{key} updated in {env_file_path}")

# Function to generate the sign parameter
def generate_sign(params, app_secret):
    # Sort parameters by key
    sorted_params = sorted(params.items())
    
    # Concatenate all key-value pairs
    sign_string = app_secret
    for key, value in sorted_params:
        sign_string += f"{key}{value}"
    
    # Append app_secret again
    sign_string += app_secret
    
    # Calculate MD5 hash
    sign = hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()
    return sign

# Prepare the request parameters
timestamp = str(int(time.time() * 1000))  # Current time in milliseconds since epoch
params = {
    "app_key": APP_KEY,
    "code": AUTH_CODE,
    "grant_type": "authorization_code",
    "sign_method": "md5",
    "timestamp": timestamp
}

# Generate the signature
signature = generate_sign(params, APP_SECRET)

# Add the signature to the parameters
params["sign"] = signature

# Construct the request URL
request_url = ALIBABA_SERVER_CALL_ENTRY + API_OPERATION

# Dummy response for demonstration purposes
response_data = {
    "access_token": "dummy_access_token"
}

# Update .env file with the dummy access_token
update_env_file('SESSION_KEY', response_data["access_token"])

# Log the API request and response
log_request_response(params, response_data, request_url, LOG_DIR)

# Log the timestamp used for debugging
print(f"Timestamp used: {timestamp}")
