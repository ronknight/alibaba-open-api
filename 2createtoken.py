import os
import requests
from dotenv import load_dotenv
import hashlib
import time
import json

# Load environment variables from .env file
load_dotenv()

# Retrieve variables from environment
APP_KEY = os.getenv('APP_KEY')
APP_SECRET = os.getenv('APP_SECRET')
AUTH_CODE = os.getenv('AUTH_CODE')

ALIBABA_SERVER_CALL_ENTRY = "https://eco.taobao.com/router/rest"
LOG_DIR = 'api_logs/'  # Directory to store log files

# Create directory if it does not exist
os.makedirs(LOG_DIR, exist_ok=True)

# Create a sign
def create_sign(params, secret):
    sorted_params = sorted(params.items())
    basestring = secret + ''.join(f'{k}{v}' for k, v in sorted_params) + secret
    return hashlib.md5(basestring.encode('utf-8')).hexdigest().upper()

# Prepare the request parameters
params = {
    'method': 'taobao.top.auth.token.create',
    'app_key': APP_KEY,
    'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
    'format': 'json',
    'v': '2.0',
    'sign_method': 'md5',
    'code': AUTH_CODE
}

# Generate the sign
params['sign'] = create_sign(params, APP_SECRET)

# Make the request
response = requests.get(ALIBABA_SERVER_CALL_ENTRY, params=params)

# Function to log API request
def log_request(request_params, log_dir):
    log_file_path = os.path.join(log_dir, "createtoken.log")
    
    with open(log_file_path, 'a') as log_file:
        log_file.write(json.dumps(request_params, indent=4) + "\n")
    
    print(f"API request logged in {log_file_path}")

# Function to log API response
def log_response(response_data, log_dir):
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    log_file_path = os.path.join(log_dir, f"createtokenresponse_{timestamp}.log")
    
    with open(log_file_path, 'w') as log_file:
        log_file.write(json.dumps(response_data, indent=4))
    
    print(f"API response logged in {log_file_path}")

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

# Check if the response is successful
if response.status_code == 200:
    response_data = response.json()
    
    # Extract access_token from the response
    try:
        token_result = response_data['top_auth_token_create_response']['token_result']
        token_result_dict = json.loads(token_result)
        access_token = token_result_dict.get('access_token')
        
        if access_token:
            # Update .env file with session_key = access_token
            update_env_file('SESSION_KEY', access_token)
        else:
            print("Access token not found in the response")
    
    except KeyError:
        print("Invalid response format, access token could not be extracted")
    
    # Log the API request and response
    log_request(params, LOG_DIR)
    log_response(response_data, LOG_DIR)
    
else:
    print(f"Failed to retrieve data: {response.status_code}")
    # Log the API request and response
    log_request(params, LOG_DIR)
    log_response(response.text, LOG_DIR)