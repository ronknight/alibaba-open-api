import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Function to get a new access token using the authorization code
def get_alibaba_access_token():
    url = "https://openapi-api.alibaba.com/oauth/token/create" 
    headers = {"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"}
    data = {
        "grant_type": "authorization_code",
        "client_id": os.getenv("APP_KEY"),
        "client_secret": os.getenv("APP_SECRET"),
        "code": os.getenv("AUTH_CODE"),
        "redirect_uri": os.getenv("REDIRECT_URI")
    }

    try:
        response = requests.post(url, headers=headers, data=data)

        # Check for error response
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            return None, None

        response_data = response.json()
        access_token = response_data.get("access_token")
        refresh_token = response_data.get("refresh_token")  # Store this for later refreshing
        return access_token, refresh_token

    except requests.exceptions.RequestException as e:
        print(f"Error getting access token: {e}")
        return None, None

# Get access token
access_token, refresh_token = get_alibaba_access_token()

if access_token:
    # Use the access token for API calls
    print("Access Token:", access_token)
    print("Refresh Token (Store this):", refresh_token)
else:
    print("Failed to obtain an access token.")
