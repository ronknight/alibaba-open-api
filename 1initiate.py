import os
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs

# Load environment variables from .env file
load_dotenv()

# Get parameters from environment variables
app_key = os.getenv('APP_KEY')
redirect_uri = os.getenv('REDIRECT_URI')

# Ensure APP_KEY and REDIRECT_URI are set correctly in your .env file
if not app_key:
    print("APP_KEY is missing or not set in the .env file.")
    exit(1)

if not redirect_uri:
    print("REDIRECT_URI is missing or not set in the .env file.")
    exit(1)

# Construct base URL
base_url = 'https://openapi-auth.alibaba.com/oauth'

# URL to redirect the user for authorization
auth_url = f"{base_url}/authorize?response_type=code&redirect_uri={redirect_uri}&client_id={app_key}"

print("Please visit the following URL to authorize the application:")
print(auth_url)

# Get the redirected URL from the user (assuming manual input for simplicity)
redirected_url = input("Please enter the redirected URL after authorization: ")

# Parse the URL to extract the query parameters
parsed_url = urlparse(redirected_url)
query_params = parse_qs(parsed_url.query)

# Extract the authorization code
auth_code = query_params.get('code', [None])[0]

# Print extracted value
print(f"Authorization Code: {auth_code}")

# Ensure AUTH_CODE is available
if not auth_code:
    print("Authorization code is missing.")
    exit(1)

# Read the current .env file
env_path = '.env'
env_vars = {}
if os.path.exists(env_path):
    with open(env_path, 'r') as env_file:
        for line in env_file:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                env_vars[key] = value

# Update the env_vars with the new value
env_vars['AUTH_CODE'] = auth_code

# Write the updated environment variables back to the .env file
with open(env_path, 'w') as env_file:
    for key, value in env_vars.items():
        env_file.write(f'{key}={value}\n')

print("Authorization code has been updated in the .env file.")
