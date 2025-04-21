#!/usr/bin/env python3
import os
import sys
import time
import json
import curses
import requests
import tempfile
import webbrowser
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
from typing import List, Callable, Tuple, Optional

def mask_sensitive_data(text: str, visible_chars: int = 4) -> str:
    """Masks sensitive data, showing only the first few characters."""
    if not text or len(text) <= visible_chars:
        return text
    return text[:visible_chars] + '*' * (len(text) - visible_chars)

class MenuItem:
    def __init__(self, name: str, description: str, action: Callable):
        self.name = name
        self.description = description
        self.action = action

class Menu:
    def __init__(self, title: str):
        self.title = title
        self.items: List[MenuItem] = []
        self.selected_index = 0
        self.running = True

    def add_item(self, name: str, description: str, action: Callable):
        self.items.append(MenuItem(name, description, action))

    def draw_menu(self, stdscr):
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        
        # Draw title
        title = f"=== {self.title} ==="
        stdscr.addstr(0, (width - len(title)) // 2, title, curses.A_BOLD)
        
        # Draw items
        for idx, item in enumerate(self.items):
            y = idx + 3
            if y >= height:
                break
                
            # Highlight selected item
            if idx == self.selected_index:
                attr = curses.A_REVERSE
            else:
                attr = curses.A_NORMAL
                
            # Draw menu item
            menu_str = f"{idx + 1}. {item.name}"
            stdscr.addstr(y, 2, menu_str, attr)
            
            # Draw description if there's room
            if len(item.description) + len(menu_str) + 4 < width:
                stdscr.addstr(y, len(menu_str) + 4, f"- {item.description}")
        
        # Draw footer
        footer = "Use ↑/↓ arrows to navigate, Enter to select, Q to quit"
        if height > 5:
            stdscr.addstr(height-2, (width - len(footer)) // 2, footer)
        
        stdscr.refresh()

    def handle_input(self, key):
        if key == curses.KEY_UP and self.selected_index > 0:
            self.selected_index -= 1
        elif key == curses.KEY_DOWN and self.selected_index < len(self.items) - 1:
            self.selected_index += 1
        elif key in [curses.KEY_ENTER, ord('\n'), ord('\r')]:
            self.items[self.selected_index].action(self.stdscr)
        elif key in [ord('q'), ord('Q')]:
            self.running = False
        elif key in range(ord('1'), ord('9')):
            idx = key - ord('1')
            if idx < len(self.items):
                self.selected_index = idx
                self.items[idx].action(self.stdscr)

    def run(self, stdscr):
        self.stdscr = stdscr  # Store stdscr for use in actions
        # Setup
        curses.curs_set(0)  # Hide cursor
        curses.start_color()
        curses.use_default_colors()
        
        while self.running:
            self.draw_menu(stdscr)
            key = stdscr.getch()
            self.handle_input(key)

def display_text_screen(stdscr, title, content_lines):
    # Clear screen and get dimensions
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    
    # Initialize color pairs if not already done
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
    
    # Draw title
    stdscr.addstr(1, (width - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(1))
    
    # Draw content
    current_y = 3
    for line in content_lines:
        if current_y >= height - 2:  # Leave room for footer
            break
            
        if isinstance(line, tuple):
            text, color = line
            stdscr.addstr(current_y, 2, text, curses.color_pair(color))
        else:
            stdscr.addstr(current_y, 2, line)
        current_y += 1
    
    # Draw footer
    footer = "Press Enter to continue..."
    if height > 5:
        stdscr.addstr(height-2, (width - len(footer)) // 2, footer, curses.color_pair(2))
    
    stdscr.refresh()
    
    # Wait for Enter key
    while True:
        key = stdscr.getch()
        if key in [curses.KEY_ENTER, ord('\n'), ord('\r')]:
            break

def display_splash_screen(stdscr):
    # Clear screen and get dimensions
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    
    # Initialize color pairs
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
    
    # Box dimensions
    box_width = 71
    box_height = 14
    start_y = (height - box_height) // 2
    start_x = (width - box_width) // 2
    
    # Draw box
    for y in range(box_height):
        for x in range(box_width):
            if y == 0 and x == 0:
                stdscr.addch(start_y + y, start_x + x, '╔', curses.color_pair(1))
            elif y == 0 and x == box_width - 1:
                stdscr.addch(start_y + y, start_x + x, '╗', curses.color_pair(1))
            elif y == box_height - 1 and x == 0:
                stdscr.addch(start_y + y, start_x + x, '╚', curses.color_pair(1))
            elif y == box_height - 1 and x == box_width - 1:
                stdscr.addch(start_y + y, start_x + x, '╝', curses.color_pair(1))
            elif y == 0 or y == box_height - 1:
                stdscr.addch(start_y + y, start_x + x, '═', curses.color_pair(1))
            elif x == 0 or x == box_width - 1:
                stdscr.addch(start_y + y, start_x + x, '║', curses.color_pair(1))
    
    # Add content
    messages = [
        ("Welcome to Alibaba Open API Command Line Interface", curses.A_BOLD, 2),
        ("Version 1.0.0", curses.color_pair(2), 4),
        ("Thank you for using our API Interface!", curses.color_pair(3), 6),
        ("This tool helps you interact with Alibaba's API endpoints easily", curses.color_pair(4), 8),
        ("and efficiently. Get started by initializing your API connection.", curses.color_pair(4), 9),
        ("For support: https://github.com/ronknight/alibaba-open-api", curses.color_pair(2), 11)
    ]
    
    for msg, attr, y_offset in messages:
        x_pos = start_x + (box_width - len(msg)) // 2
        stdscr.addstr(start_y + y_offset, x_pos, msg, attr)
    
    stdscr.refresh()
    time.sleep(2)

def display_exit_screen(stdscr):
    # Clear screen and get dimensions
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    
    # Box dimensions
    box_width = 71
    box_height = 11
    start_y = (height - box_height) // 2
    start_x = (width - box_width) // 2
    
    # Draw box
    for y in range(box_height):
        for x in range(box_width):
            if y == 0 and x == 0:
                stdscr.addch(start_y + y, start_x + x, '╔', curses.color_pair(1))
            elif y == 0 and x == box_width - 1:
                stdscr.addch(start_y + y, start_x + x, '╗', curses.color_pair(1))
            elif y == box_height - 1 and x == 0:
                stdscr.addch(start_y + y, start_x + x, '╚', curses.color_pair(1))
            elif y == box_height - 1 and x == box_width - 1:
                stdscr.addch(start_y + y, start_x + x, '╝', curses.color_pair(1))
            elif y == 0 or y == box_height - 1:
                stdscr.addch(start_y + y, start_x + x, '═', curses.color_pair(1))
            elif x == 0 or x == box_width - 1:
                stdscr.addch(start_y + y, start_x + x, '║', curses.color_pair(1))
    
    # Add content
    messages = [
        ("Thank You for Using Our Application!", curses.A_BOLD, 2),
        ("Your session has been successfully completed", curses.color_pair(3), 4),
        ("We hope to see you again soon!", curses.color_pair(4), 6),
        ("For updates and support: github.com/ronknight/alibaba-open-api", curses.color_pair(2), 8)
    ]
    
    for msg, attr, y_offset in messages:
        x_pos = start_x + (box_width - len(msg)) // 2
        stdscr.addstr(start_y + y_offset, x_pos, msg, attr)
    
    stdscr.refresh()
    time.sleep(1.5)

def display_category_usage(stdscr):
    content = [
        "",
        ("Available Endpoints:", 1),
        "",
        ("1. Get Category Info:", 2),
        "   python product_category_get.py <category_id>",
        "",
        ("2. Get Root Categories:", 2),
        "   python product_category_get_root.py",
        "",
        ("3. Get Category ID Mapping:", 2),
        "   python product_category_id_mapping.py <category_id>"
    ]
    display_text_screen(stdscr, "Product Category API Usage", content)

def display_inventory_usage(stdscr):
    content = [
        "",
        ("Available Endpoints:", 1),
        "",
        ("1. Get Inventory:", 2),
        "   python product_inventory_get.py --product_id <id>",
        "",
        ("2. Update Inventory:", 2),
        "   python product_inventory_update.py --product_id <id> --inventory <amount>"
    ]
    display_text_screen(stdscr, "Inventory Management API Usage", content)

def display_photo_usage(stdscr):
    content = [
        "",
        ("Available Endpoints:", 1),
        "",
        ("1. List Photo Groups:", 2),
        "   python product_photobank_group_list.py",
        "",
        ("2. Upload Photo:", 2),
        "   python product_photobank_upload.py --file <path> [--group_id <id>]",
        "",
        ("3. List Photos:", 2),
        "   python product_photobank_list.py [--group_id <id>]",
        "",
        ("4. Manage Photo Groups:", 2),
        "   python product_photobank_group_operate.py --action <create|update|delete> --name <group_name>"
    ]
    display_text_screen(stdscr, "Photo Management API Usage", content)

def display_product_list_usage(stdscr):
    content = [
        "",
        ("Basic Product Operations:", 1),
        "",
        ("1. List Products:", 2),
        "   python product_list.py [--current_page <num>] [--page_size <num>] [--subject <text>]",
        "",
        ("2. List All Products:", 2),
        "   python product_list_all.py",
        "",
        ("3. Get Product Details:", 2),
        "   python product_get.py --product_id <id>",
        "",
        ("Product Schema Operations:", 1),
        "",
        ("1. Get Product Schema:", 2),
        "   python product_schema_get.py --category_id <id>",
        ("2. Add Product Schema:", 2),
        "   python product_schema_add.py --category_id <id> --schema <json_data>",
        ("3. Update Product Schema:", 2),
        "   python product_schema_update.py --product_id <id> --schema <json_data>",
        ("4. Get Schema Levels:", 2),
        "   python product_schema_level_get.py --category_id <id>",
        "",
        ("Other Product Operations:", 1),
        "",
        ("1. Get Product Score:", 2),
        "   python product_score_get.py --product_id <id>",
        ("2. Update Product Display:", 2),
        "   python product_update_display.py --product_id <id> --display_status <status>",
        ("3. Check Product Availability:", 2),
        "   python product_available_get.py --product_id <id>"
    ]
    display_text_screen(stdscr, "Product Management API Usage", content)

def initialize_api(stdscr):
    import os
    from dotenv import load_dotenv
    from urllib.parse import urlparse, parse_qs
    
    # Clear screen and setup
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    current_y = 2
    
    # Load environment variables
    load_dotenv()
    app_key = os.getenv('APP_KEY')
    redirect_uri = os.getenv('REDIRECT_URI')
    
    # Check environment variables
    if not app_key or not redirect_uri:
        stdscr.addstr(current_y, 2, "Error: APP_KEY or REDIRECT_URI missing in .env file", curses.color_pair(2))
        stdscr.refresh()
        stdscr.getch()
        return
    
    # Construct authorization URL (masking app_key in display)
    base_url = 'https://openapi-auth.alibaba.com/oauth'
    auth_url = f"{base_url}/authorize?response_type=code&redirect_uri={redirect_uri}&client_id={app_key}"
    display_url = f"{base_url}/authorize?response_type=code&redirect_uri={redirect_uri}&client_id={mask_sensitive_data(app_key)}"
    
    # Display instructions
    stdscr.addstr(current_y, 2, "Please visit the following URL to authorize the application:", curses.color_pair(4))
    current_y += 2
    
    # Display masked URL
    stdscr.addstr(current_y, 2, display_url, curses.color_pair(1))
    current_y += 2
    
    stdscr.addstr(current_y, 2, "Press 'o' to open in browser, or any other key to continue...", curses.color_pair(4))
    stdscr.refresh()
    
    # Handle user input
    ch = stdscr.getch()
    if ch == ord('o'):
        webbrowser.open(auth_url)
    
    # Clear screen for next step
    stdscr.clear()
    current_y = 2
    
    # Get redirected URL from user
    stdscr.addstr(current_y, 2, "After authorization, paste the redirected URL here:", curses.color_pair(4))
    current_y += 2
    
    # Create a temporary file for URL input
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        curses.echo()
        curses.curs_set(1)
        stdscr.addstr(current_y, 2, "> ")
        redirected_url = stdscr.getstr().decode('utf-8')
        temp_file.write(redirected_url)
    
    curses.noecho()
    curses.curs_set(0)
    
    # Parse the URL and extract auth code
    try:
        parsed_url = urlparse(redirected_url)
        query_params = parse_qs(parsed_url.query)
        auth_code = query_params.get('code', [None])[0]
        
        if not auth_code:
            raise ValueError("No authorization code found in URL")
        
        # Update .env file with auth code
        env_path = '.env'
        env_content = []
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                env_content = f.readlines()
        
        # Update or add auth code
        auth_code_line = f"AUTH_CODE={auth_code}\n"
        auth_code_found = False
        for i, line in enumerate(env_content):
            if line.startswith('AUTH_CODE='):
                env_content[i] = auth_code_line
                auth_code_found = True
                break
        if not auth_code_found:
            env_content.append(auth_code_line)
        
        with open(env_path, 'w') as f:
            f.writelines(env_content)
        
        # Display success message with masked auth code
        current_y += 2
        stdscr.addstr(current_y, 2, "Authorization code received successfully!", curses.color_pair(3))
        current_y += 1
        masked_code = mask_sensitive_data(auth_code)
        stdscr.addstr(current_y, 2, f"Auth Code: {masked_code}", curses.color_pair(4))
        
    except Exception as e:
        current_y += 2
        stdscr.addstr(current_y, 2, f"Error: {str(e)}", curses.color_pair(2))
    
    current_y += 2
    stdscr.addstr(current_y, 2, "Press any key to continue...", curses.color_pair(4))
    stdscr.refresh()
    stdscr.getch()

def create_token(stdscr):
    # Clear screen and setup
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    current_y = 2
    
    # Load environment variables
    load_dotenv()
    app_key = os.getenv('APP_KEY')
    app_secret = os.getenv('APP_SECRET')
    auth_code = os.getenv('AUTH_CODE')
    redirect_uri = os.getenv('REDIRECT_URI')
    
    # Check environment variables
    if not all([app_key, app_secret, auth_code, redirect_uri]):
        stdscr.addstr(current_y, 2, "Error: Required environment variables missing in .env file", curses.color_pair(2))
        current_y += 2
        stdscr.addstr(current_y, 2, "Please ensure APP_KEY, APP_SECRET, AUTH_CODE, and REDIRECT_URI are set", curses.color_pair(2))
        stdscr.refresh()
        stdscr.getch()
        return
    
    try:
        # API endpoint for token creation
        url = "https://openapi-auth.alibaba.com/oauth/token"
        
        # Request parameters
        params = {
            'grant_type': 'authorization_code',
            'client_id': app_key,
            'client_secret': app_secret,
            'code': auth_code,
            'redirect_uri': redirect_uri
        }
        
        # Display status
        stdscr.addstr(current_y, 2, "Creating access token...", curses.color_pair(4))
        stdscr.refresh()
        
        # Make the request
        response = requests.post(url, params=params)
        response_data = response.json()
        
        current_y += 2
        if response.status_code == 200 and 'access_token' in response_data:
            # Update .env file with new tokens
            env_path = '.env'
            env_content = []
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    env_content = f.readlines()
            
            # Update or add tokens
            new_vars = {
                'ACCESS_TOKEN': response_data['access_token'],
                'REFRESH_TOKEN': response_data.get('refresh_token', ''),
                'TOKEN_EXPIRY': str(response_data.get('expires_in', ''))
            }
            
            for key, value in new_vars.items():
                line = f"{key}={value}\n"
                found = False
                for i, env_line in enumerate(env_content):
                    if env_line.startswith(f"{key}="):
                        env_content[i] = line
                        found = True
                        break
                if not found:
                    env_content.append(line)
            
            with open(env_path, 'w') as f:
                f.writelines(env_content)
            
            # Display success message with masked data
            stdscr.addstr(current_y, 2, "Access token created successfully!", curses.color_pair(3))
            current_y += 2
            masked_token = mask_sensitive_data(response_data['access_token'])
            stdscr.addstr(current_y, 2, f"Access Token: {masked_token}", curses.color_pair(4))
            current_y += 1
            stdscr.addstr(current_y, 2, f"Expires in: {response_data.get('expires_in', 'N/A')} seconds", curses.color_pair(4))
            
        else:
            # Display error message
            stdscr.addstr(current_y, 2, "Error creating access token:", curses.color_pair(2))
            current_y += 1
            error_msg = response_data.get('error_description', response_data.get('error', 'Unknown error'))
            stdscr.addstr(current_y, 2, error_msg, curses.color_pair(2))
    
    except Exception as e:
        stdscr.addstr(current_y, 2, f"Error: {str(e)}", curses.color_pair(2))
    
    # Display footer
    current_y += 2
    stdscr.addstr(height-2, 2, "Press any key to continue...", curses.color_pair(4))
    stdscr.refresh()
    stdscr.getch()

def refresh_token(stdscr):
    # Clear screen and setup
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    current_y = 2
    
    # Load environment variables
    load_dotenv()
    app_key = os.getenv('APP_KEY')
    app_secret = os.getenv('APP_SECRET')
    refresh_token_val = os.getenv('REFRESH_TOKEN')
    
    # Check environment variables
    if not all([app_key, app_secret, refresh_token_val]):
        stdscr.addstr(current_y, 2, "Error: Required environment variables missing in .env file", curses.color_pair(2))
        current_y += 2
        stdscr.addstr(current_y, 2, "Please ensure APP_KEY, APP_SECRET, and REFRESH_TOKEN are set", curses.color_pair(2))
        stdscr.refresh()
        stdscr.getch()
        return
    
    try:
        # API endpoint for token refresh
        url = "https://openapi-auth.alibaba.com/oauth/token"
        
        # Request parameters
        params = {
            'grant_type': 'refresh_token',
            'client_id': app_key,
            'client_secret': app_secret,
            'refresh_token': refresh_token_val
        }
        
        # Display status
        stdscr.addstr(current_y, 2, "Refreshing access token...", curses.color_pair(4))
        stdscr.refresh()
        
        # Make the request
        response = requests.post(url, params=params)
        response_data = response.json()
        
        current_y += 2
        if response.status_code == 200 and 'access_token' in response_data:
            # Update .env file with new tokens
            env_path = '.env'
            env_content = []
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    env_content = f.readlines()
            
            # Update or add tokens
            new_vars = {
                'ACCESS_TOKEN': response_data['access_token'],
                'REFRESH_TOKEN': response_data.get('refresh_token', ''),
                'TOKEN_EXPIRY': str(response_data.get('expires_in', ''))
            }
            
            for key, value in new_vars.items():
                line = f"{key}={value}\n"
                found = False
                for i, env_line in enumerate(env_content):
                    if env_line.startswith(f"{key}="):
                        env_content[i] = line
                        found = True
                        break
                if not found:
                    env_content.append(line)
            
            with open(env_path, 'w') as f:
                f.writelines(env_content)
            
            # Display success message with masked data
            stdscr.addstr(current_y, 2, "Access token refreshed successfully!", curses.color_pair(3))
            current_y += 2
            masked_token = mask_sensitive_data(response_data['access_token'])
            stdscr.addstr(current_y, 2, f"New Access Token: {masked_token}", curses.color_pair(4))
            current_y += 1
            if 'expires_in' in response_data:
                stdscr.addstr(current_y, 2, f"Expires in: {response_data['expires_in']} seconds", curses.color_pair(4))
                current_y += 1
            
        else:
            # Display error message
            stdscr.addstr(current_y, 2, "Error refreshing access token:", curses.color_pair(2))
            current_y += 1
            error_msg = response_data.get('error_description', response_data.get('error', 'Unknown error'))
            stdscr.addstr(current_y, 2, error_msg, curses.color_pair(2))
    
    except Exception as e:
        stdscr.addstr(current_y, 2, f"Error: {str(e)}", curses.color_pair(2))
    
    # Display footer
    current_y += 2
    stdscr.addstr(height-2, 2, "Press any key to continue...", curses.color_pair(4))
    stdscr.refresh()
    stdscr.getch()

def get_product_list(stdscr):
    display_product_list_usage(stdscr)

def get_product_categories(stdscr):
    display_category_usage(stdscr)

def update_product_inventory(stdscr):
    display_inventory_usage(stdscr)

def upload_product_photo(stdscr):
    display_photo_usage(stdscr)

def get_user_input(stdscr, prompt, y_pos):
    curses.echo()  # Show typed characters
    curses.curs_set(1)  # Show cursor
    height, width = stdscr.getmaxyx()
    
    # Display prompt
    stdscr.addstr(y_pos, 2, prompt)
    stdscr.refresh()
    
    # Create input window
    input_win = curses.newwin(1, width-len(prompt)-4, y_pos, len(prompt) + 3)
    input_win.refresh()
    
    # Get input
    input_text = input_win.getstr().decode('utf-8')
    
    curses.noecho()  # Disable echo
    curses.curs_set(0)  # Hide cursor
    return input_text

def main():
    # Add error handling and logging
    import logging
    logging.basicConfig(
        level=logging.DEBUG,
        filename='cli_menu.log',
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    def run_application(stdscr):
        try:
            # Initialize color pairs
            curses.start_color()
            curses.use_default_colors()
            
            # Initialize color pairs
            curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
            
            # Show splash screen
            display_splash_screen(stdscr)
            
            # Initialize the menu
            menu = Menu("Alibaba Open API CLI Interface")
            
            # Authentication Menu Items
            menu.add_item("Initialize API", "Setup initial API connection", initialize_api)
            menu.add_item("Create Token", "Generate new access token", create_token)
            menu.add_item("Refresh Token", "Refresh existing access token", refresh_token)
            
            # Product Management Menu Items
            menu.add_item("List Products", "Get list of products", get_product_list)
            menu.add_item("Product Categories", "Get product categories", get_product_categories)
            menu.add_item("Update Inventory", "Update product inventory", update_product_inventory)
            menu.add_item("Upload Photos", "Upload product photos", upload_product_photo)
            
            # Run the menu
            menu.run(stdscr)
            
            # Show exit screen
            display_exit_screen(stdscr)
        except Exception as e:
            logging.error(f"Error in run_application: {str(e)}", exc_info=True)
            raise

    try:
        logging.info("Starting application with curses wrapper")
        curses.wrapper(run_application)
    except KeyboardInterrupt:
        logging.info("Application terminated by user (KeyboardInterrupt)")
    except Exception as e:
        logging.error(f"Critical error in main: {str(e)}", exc_info=True)
        print(f"An error occurred. Check cli_menu.log for details.")
    finally:
        logging.info("Application terminated")

if __name__ == "__main__":
    main()
