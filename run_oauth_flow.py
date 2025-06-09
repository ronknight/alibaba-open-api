#!/usr/bin/env python3
"""
Automated OAuth Flow for Alibaba Open API
This script runs the complete OAuth flow:
1. Gets authorization code (1initiate.py)
2. Creates access tokens (2createtoken.py)
3. Optionally refreshes tokens (3refreshtoken.py) - user choice
"""

import os
import subprocess
import sys
from datetime import datetime

def run_script(script_name, description):
    """Run a Python script and handle errors."""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Script: {script_name}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, check=True)
        print(f"✓ {script_name} executed successfully!")
        print(result.stdout)
        if result.stderr:
            print("Warnings:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error running {script_name}: {e}")
        print("Error output:", e.stderr)
        return False
    except FileNotFoundError:
        print(f"✗ Could not find {script_name} in the current directory")
        return False

def main():
    print("🚀 Starting Alibaba OAuth Flow Automation")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Run authorization flow
    if not run_script("1initiate.py", "Authorization Code Generation"):
        print("❌ Failed at authorization step. Exiting.")
        sys.exit(1)
    
    # Step 2: Create tokens
    if not run_script("2createtoken.py", "Access Token Creation"):
        print("❌ Failed at token creation step. Exiting.")
        sys.exit(1)
    
    # Step 3: Optional token refresh
    print("\n" + "="*50)
    choice = input("Do you want to run token refresh (3refreshtoken.py)? [y/N]: ").strip().lower()
    if choice in ['y', 'yes']:
        if run_script("3refreshtoken.py", "Token Refresh"):
            print("✅ Complete OAuth flow finished successfully!")
        else:
            print("⚠️ Token refresh failed, but access tokens are available.")
    else:
        print("✅ OAuth flow completed! Tokens are ready for use.")
    
    print(f"\nProcess completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
