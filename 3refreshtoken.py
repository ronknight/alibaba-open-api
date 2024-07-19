import os
import requests
import hashlib
import hmac
import time
from urllib.parse import urlencode
from dotenv import load_dotenv, set_key
import json
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()

# Function to generate the signature
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

# Retrieve parameters from environment
APP_KEY = os.getenv('APP_KEY')
APP_SECRET = os.getenv('APP_SECRET')
REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')
ALIBABA_SERVER_CALL_ENTRY = "https://openapi-api.alibaba.com/rest"
API_OPERATION = "/auth/token/refresh"  # Specify your API operation endpoint here

# Prepare the request parameters
timestamp = str(int(time.time() * 1000))  # Replace with your actual timestamp logic if needed
params = {
    "app_key": APP_KEY,
    "refresh_token": REFRESH_TOKEN,
    "sign_method": "sha256",
    "timestamp": timestamp
}

# Generate the signature
signature = generate_signature(params, APP_SECRET, API_OPERATION)

# Add the generated signature to the params dictionary
params['sign'] = signature

# Construct the formatted output
formatted_output = f"hex(sha256('{API_OPERATION}'"
for k, v in sorted(params.items()):
    formatted_output += f"{k}{v}"
formatted_output += f"))={signature}"

print("Formatted Output:")
print(formatted_output)

try:
    # Make the POST request
    response = requests.post(f"{ALIBABA_SERVER_CALL_ENTRY}{API_OPERATION}", data=params)
    
    # Handle the response
    if response.status_code == 200:
        response_data = response.json()
        print("\nResponse:")
        print(response_data)
        
        # Extract values from the response
        access_token = response_data.get('access_token')
        refresh_token = response_data.get('refresh_token')
        account = response_data.get('account')
        expires_in = response_data.get('expires_in')
        refresh_expires_in = response_data.get('refresh_expires_in')

        if access_token and refresh_token and account and expires_in and refresh_expires_in:
            # Convert expires_in and refresh_expires_in to human-readable format
            expires_at = (datetime.now() + timedelta(seconds=expires_in)).strftime("%Y-%m-%d %H:%M:%S")
            refresh_expires_at = (datetime.now() + timedelta(seconds=refresh_expires_in)).strftime("%Y-%m-%d %H:%M:%S")

            # Save the values to the .env file
            env_file = '.env'
            set_key(env_file, 'ACCESS_TOKEN', access_token)
            set_key(env_file, 'REFRESH_TOKEN', refresh_token)
            set_key(env_file, 'ACCOUNT', account)
            set_key(env_file, 'EXPIRES_AT', expires_at)
            set_key(env_file, 'REFRESH_EXPIRES_AT', refresh_expires_at)
            print("\nTokens and other details saved to .env file.")
        else:
            print("\nSome expected values were not found in the response.")

        # Log the response to a JSON file with a timestamp
        log_dir = 'api_logs'
        os.makedirs(log_dir, exist_ok=True)
        timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
        log_file_path = os.path.join(log_dir, f"api_response_{timestamp_str}.json")
        with open(log_file_path, 'w') as log_file:
            json.dump(response_data, log_file, indent=4)
        print(f"\nResponse logged to {log_file_path}")
    else:
        print(f"\nRequest failed with status code {response.status_code}")
        print("Response:", response.text)

except requests.exceptions.RequestException as e:
    print(f"\nRequest error: {e}")
