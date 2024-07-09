# -*- coding: utf-8 -*-
import os
import time
import hashlib
import hmac
import requests
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app_key = os.getenv('APP_KEY')
app_secret = os.getenv('APP_SECRET')
session_key = os.getenv('SESSION_KEY')
url = os.getenv('URL')

def get_timestamp():
    return time.strftime('%Y-%m-%d %H:%M:%S')

def sign(params, secret):
    sorted_params = sorted(params.items())
    base_string = secret + ''.join(f'{k}{v}' for k, v in sorted_params) + secret
    hash = hmac.new(secret.encode('utf-8'), base_string.encode('utf-8'), hashlib.md5).hexdigest().upper()
    return hash

params = {
    'app_key': app_key,
    'format': 'json',
    'method': 'alibaba.icbu.product.get',
    'partner_id': 'apidoc',
    'session': session_key,
    'sign_method': 'hmac',
    'timestamp': get_timestamp(),
    'v': '2.0',
    'language': 'ENGLISH',
    'product_id': '6edvniewvnewovn'
}

# Generate the signature
params['sign'] = sign(params, app_secret)

# Encode parameters for the POST request
encoded_params = '&'.join(f'{k}={quote_plus(str(v))}' for k, v in params.items())

# Make the POST request
response = requests.post(url, headers={'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}, data=encoded_params)

# Debug: print status code and response text
print(f"Status Code: {response.status_code}")
print(f"Response Text: {response.text}")

# Check for valid JSON response
try:
    response_json = response.json()
    print(response_json)
except requests.exceptions.JSONDecodeError:
    print("Response is not in JSON format.")
except Exception as e:
    print(f"An error occurred: {e}")
