#!/usr/bin/env python3
import os
import sys
import time
import json
import curses
import hmac
import hashlib
import requests
import tempfile
import webbrowser
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv, set_key
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
        self.has_colors = False
        
    def add_item(self, name: str, description: str, action: Callable):
        """Add a menu item to the menu.
        
        Args:
            name: The name of the menu item to display
            description: A short description of what the menu item does
            action: A callable that takes a curses window as argument and performs the menu action
        """
        self.items.append(MenuItem(name, description, action))
        
    def init_colors(self):
        try:
            if curses.has_colors():
                curses.start_color()
                curses.use_default_colors()
                curses.init_pair(1, curses.COLOR_CYAN, -1)
                curses.init_pair(2, curses.COLOR_YELLOW, -1)
                curses.init_pair(3, curses.COLOR_GREEN, -1)
                curses.init_pair(4, curses.COLOR_BLUE, -1)
                self.has_colors = True
        except:
            self.has_colors = False

    def draw_menu(self, stdscr):
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        
        # Draw title
        title = f"=== {self.title} ==="
        try:
            stdscr.addstr(0, (width - len(title)) // 2, title, curses.A_BOLD)
        except:
            try:
                stdscr.addstr(0, (width - len(title)) // 2, title)
            except:
                pass
        
        # Draw items
        for idx, item in enumerate(self.items):
            y = idx + 3
            if y >= height:
                break
            
            try:
                # Highlight selected item
                menu_str = f"{idx + 1}. {item.name}"
                if idx == self.selected_index:
                    attr = curses.A_REVERSE
                else:
                    attr = curses.A_NORMAL
                    
                stdscr.addstr(y, 2, menu_str, attr)
                
                # Draw description if there's room
                if len(item.description) + len(menu_str) + 4 < width:
                    desc_attr = curses.color_pair(4) if self.has_colors else curses.A_NORMAL
                    stdscr.addstr(y, len(menu_str) + 4, f"- {item.description}", desc_attr)
            except:
                continue
        
        # Draw footer
        try:
            footer = "Use ↑/↓ arrows to navigate, Enter to select, Q to quit"
            if height > 5:
                footer_attr = curses.color_pair(2) if self.has_colors else curses.A_NORMAL
                stdscr.addstr(height-2, (width - len(footer)) // 2, footer, footer_attr)
        except:
            pass
        
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
        self.init_colors()  # Initialize colors
        
        while self.running:
            try:
                self.draw_menu(stdscr)
                key = stdscr.getch()
                self.handle_input(key)
            except:
                # If there's an error in the menu loop, wait a bit and try again
                time.sleep(0.1)

def display_text_screen(stdscr, title, content_lines):
    # Clear screen and get dimensions
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    has_colors = False
    
    try:
        # Initialize color pairs if supported
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(1, curses.COLOR_CYAN, -1)
            curses.init_pair(2, curses.COLOR_YELLOW, -1)
            curses.init_pair(3, curses.COLOR_GREEN, -1)
            curses.init_pair(4, curses.COLOR_BLUE, -1)
            has_colors = True
    except:
        pass
    
    # Draw title
    try:
        title_attr = curses.A_BOLD | (curses.color_pair(1) if has_colors else 0)
        stdscr.addstr(1, (width - len(title)) // 2, title, title_attr)
    except:
        try:
            stdscr.addstr(1, (width - len(title)) // 2, title)
        except:
            pass
    
    # Draw content
    current_y = 3
    for line in content_lines:
        if current_y >= height - 2:  # Leave room for footer
            break
        
        try:
            if isinstance(line, tuple):
                text, color = line
                attr = curses.color_pair(color) if has_colors else curses.A_NORMAL
                stdscr.addstr(current_y, 2, text, attr)
            else:
                stdscr.addstr(current_y, 2, line)
            current_y += 1
        except:
            current_y += 1
            continue
    
    # Draw footer
    try:
        footer = "Press Enter to continue..."
        if height > 5:
            footer_attr = curses.color_pair(2) if has_colors else curses.A_NORMAL
            stdscr.addstr(height-2, (width - len(footer)) // 2, footer, footer_attr)
    except:
        pass
    
    stdscr.refresh()
    
    # Wait for Enter key
    while True:
        try:
            key = stdscr.getch()
            if key in [curses.KEY_ENTER, ord('\n'), ord('\r')]:
                break
        except:
            time.sleep(0.1)

def display_splash_screen(stdscr):
    # Clear screen and get dimensions
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    has_colors = False
    
    try:
        # Initialize color pairs if supported
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(1, curses.COLOR_CYAN, -1)
            curses.init_pair(2, curses.COLOR_YELLOW, -1)
            curses.init_pair(3, curses.COLOR_GREEN, -1)
            curses.init_pair(4, curses.COLOR_BLUE, -1)
            has_colors = True
    except:
        pass
    
    # Box dimensions
    box_width = 71
    box_height = 14
    start_y = (height - box_height) // 2
    start_x = (width - box_width) // 2
    
    # Draw box
    try:
        for y in range(box_height):
            for x in range(box_width):
                attr = curses.color_pair(1) if has_colors else curses.A_NORMAL
                if y == 0 and x == 0:
                    stdscr.addch(start_y + y, start_x + x, '╔', attr)
                elif y == 0 and x == box_width - 1:
                    stdscr.addch(start_y + y, start_x + x, '╗', attr)
                elif y == box_height - 1 and x == 0:
                    stdscr.addch(start_y + y, start_x + x, '╚', attr)
                elif y == box_height - 1 and x == box_width - 1:
                    stdscr.addch(start_y + y, start_x + x, '╝', attr)
                elif y == 0 or y == box_height - 1:
                    stdscr.addch(start_y + y, start_x + x, '═', attr)
                elif x == 0 or x == box_width - 1:
                    stdscr.addch(start_y + y, start_x + x, '║', attr)
    except:
        pass
    
    # Add content
    messages = [
        ("Welcome to Alibaba Open API Command Line Interface", curses.A_BOLD, 2),
        ("Version 1.0.0", curses.color_pair(2) if has_colors else curses.A_NORMAL, 4),
        ("Thank you for using our API Interface!", curses.color_pair(3) if has_colors else curses.A_NORMAL, 6),
        ("This tool helps you interact with Alibaba's API endpoints easily", curses.color_pair(4) if has_colors else curses.A_NORMAL, 8),
        ("and efficiently. Get started by initializing your API connection.", curses.color_pair(4) if has_colors else curses.A_NORMAL, 9),
        ("For support: https://github.com/ronknight/alibaba-open-api", curses.color_pair(2) if has_colors else curses.A_NORMAL, 11)
    ]
    
    for msg, attr, y_offset in messages:
        try:
            x_pos = start_x + (box_width - len(msg)) // 2
            stdscr.addstr(start_y + y_offset, x_pos, msg, attr)
        except:
            continue
    
    stdscr.refresh()
    time.sleep(2)

def display_exit_screen(stdscr):
    # Clear screen and get dimensions
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    has_colors = False
    
    try:
        # Initialize color pairs if supported
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(1, curses.COLOR_CYAN, -1)
            curses.init_pair(2, curses.COLOR_YELLOW, -1)
            curses.init_pair(3, curses.COLOR_GREEN, -1)
            curses.init_pair(4, curses.COLOR_BLUE, -1)
            has_colors = True
    except:
        pass
    
    # Box dimensions
    box_width = 71
    box_height = 11
    start_y = (height - box_height) // 2
    start_x = (width - box_width) // 2
    
    # Draw box
    try:
        for y in range(box_height):
            for x in range(box_width):
                attr = curses.color_pair(1) if has_colors else curses.A_NORMAL
                if y == 0 and x == 0:
                    stdscr.addch(start_y + y, start_x + x, '╔', attr)
                elif y == 0 and x == box_width - 1:
                    stdscr.addch(start_y + y, start_x + x, '╗', attr)
                elif y == box_height - 1 and x == 0:
                    stdscr.addch(start_y + y, start_x + x, '╚', attr)
                elif y == box_height - 1 and x == box_width - 1:
                    stdscr.addch(start_y + y, start_x + x, '╝', attr)
                elif y == 0 or y == box_height - 1:
                    stdscr.addch(start_y + y, start_x + x, '═', attr)
                elif x == 0 or x == box_width - 1:
                    stdscr.addch(start_y + y, start_x + x, '║', attr)
    except:
        pass
    
    # Add content
    messages = [
        ("Thank You for Using Our Application!", curses.A_BOLD, 2),
        ("Your session has been successfully completed", curses.color_pair(3) if has_colors else curses.A_NORMAL, 4),
        ("We hope to see you again soon!", curses.color_pair(4) if has_colors else curses.A_NORMAL, 6),
        ("For updates and support: github.com/ronknight/alibaba-open-api", curses.color_pair(2) if has_colors else curses.A_NORMAL, 8)
    ]
    
    for msg, attr, y_offset in messages:
        try:
            x_pos = start_x + (box_width - len(msg)) // 2
            stdscr.addstr(start_y + y_offset, x_pos, msg, attr)
        except:
            continue
    
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
    
    try:
        # Initialize color pairs if supported
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(1, curses.COLOR_CYAN, -1)
            curses.init_pair(2, curses.COLOR_YELLOW, -1)
            curses.init_pair(3, curses.COLOR_GREEN, -1)
            curses.init_pair(4, curses.COLOR_BLUE, -1)
    except:
        pass
    
    # Load environment variables
    load_dotenv()
    app_key = os.getenv('APP_KEY')
    redirect_uri = os.getenv('REDIRECT_URI')
    
    # Check environment variables
    if not app_key or not redirect_uri:
        try:
            stdscr.addstr(current_y, 2, "Error: APP_KEY or REDIRECT_URI missing in .env file", 
                         curses.color_pair(2) if curses.has_colors() else curses.A_NORMAL)
            stdscr.refresh()
            stdscr.getch()
            return
        except:
            return
    
    # Construct authorization URL (masking app_key in display)
    base_url = 'https://openapi-auth.alibaba.com/oauth'
    auth_url = f"{base_url}/authorize?response_type=code&redirect_uri={redirect_uri}&client_id={app_key}"
    display_url = f"{base_url}/authorize?response_type=code&redirect_uri={redirect_uri}&client_id={mask_sensitive_data(app_key)}"
    
    try:
        # Display instructions
        attr = curses.color_pair(4) if curses.has_colors() else curses.A_NORMAL
        stdscr.addstr(current_y, 2, "Please visit the following URL to authorize the application:", attr)
        current_y += 2
        
        # Display masked URL
        url_attr = curses.color_pair(1) if curses.has_colors() else curses.A_NORMAL
        stdscr.addstr(current_y, 2, display_url, url_attr)
        current_y += 2
        
        stdscr.addstr(current_y, 2, "Press 'o' to open in browser, or any other key to continue...", attr)
        stdscr.refresh()
    except:
        pass
    
    # Handle user input
    try:
        ch = stdscr.getch()
        if ch == ord('o'):
            webbrowser.open(auth_url)
    except:
        pass
    
    # Clear screen for next step
    stdscr.clear()
    current_y = 2
    
    try:
        # Get redirected URL from user
        attr = curses.color_pair(4) if curses.has_colors() else curses.A_NORMAL
        stdscr.addstr(current_y, 2, "After authorization, paste the redirected URL here:", attr)
        current_y += 2
    except:
        pass
    
    # Create a temporary file for URL input
    redirected_url = ""
    try:
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            curses.echo()
            curses.curs_set(1)
            stdscr.addstr(current_y, 2, "> ")
            redirected_url = stdscr.getstr().decode('utf-8')
            temp_file.write(redirected_url)
    except:
        pass
    finally:
        curses.noecho()
        curses.curs_set(0)
    
    if not redirected_url:
        return
    
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
        success_attr = curses.color_pair(3) if curses.has_colors() else curses.A_NORMAL
        info_attr = curses.color_pair(4) if curses.has_colors() else curses.A_NORMAL
        
        stdscr.addstr(current_y, 2, "Authorization code received successfully!", success_attr)
        current_y += 1
        masked_code = mask_sensitive_data(auth_code)
        stdscr.addstr(current_y, 2, f"Auth Code: {masked_code}", info_attr)
        
    except Exception as e:
        current_y += 2
        error_attr = curses.color_pair(2) if curses.has_colors() else curses.A_NORMAL
        try:
            stdscr.addstr(current_y, 2, f"Error: {str(e)}", error_attr)
        except:
            pass
    
    # Final prompt
    try:
        current_y += 2
        prompt_attr = curses.color_pair(4) if curses.has_colors() else curses.A_NORMAL
        stdscr.addstr(current_y, 2, "Press any key to continue...", prompt_attr)
        stdscr.refresh()
        stdscr.getch()
    except:
        pass

def create_token(stdscr):
    # Clear screen and setup
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    current_y = 2
    has_colors = False
    
    try:
        # Initialize color pairs if supported
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(1, curses.COLOR_CYAN, -1)
            curses.init_pair(2, curses.COLOR_YELLOW, -1)
            curses.init_pair(3, curses.COLOR_GREEN, -1)
            curses.init_pair(4, curses.COLOR_BLUE, -1)
            has_colors = True
    except:
        pass
    
    try:
        # Load environment variables
        load_dotenv()
        app_key = os.getenv('APP_KEY')
        app_secret = os.getenv('APP_SECRET')
        auth_code = os.getenv('AUTH_CODE')
        
        # Check environment variables
        if not all([app_key, app_secret, auth_code]):
            error_attr = curses.color_pair(2) if has_colors else curses.A_NORMAL
            stdscr.addstr(current_y, 2, "Error: Required environment variables missing in .env file", error_attr)
            current_y += 2
            stdscr.addstr(current_y, 2, "Please ensure APP_KEY, APP_SECRET, and AUTH_CODE are set", error_attr)
            stdscr.refresh()
            stdscr.getch()
            return
        
        # API endpoint setup
        ALIBABA_SERVER_CALL_ENTRY = "https://openapi-api.alibaba.com/rest"
        API_OPERATION = "/auth/token/create"
        url = f"{ALIBABA_SERVER_CALL_ENTRY}{API_OPERATION}"

        # Generate timestamp and prepare request
        timestamp = str(int(time.time() * 1000))
        params = {
            "app_key": app_key,
            "code": auth_code,
            "sign_method": "sha256",
            "timestamp": timestamp
        }

        # Generate signature
        def generate_signature(params, secret_key, api_operation):
            sorted_params = sorted(params.items())
            concatenated_string = api_operation
            for k, v in sorted_params:
                concatenated_string += f"{k}{v}"
            hashed = hmac.new(secret_key.encode('utf-8'), 
                            concatenated_string.encode('utf-8'), 
                            hashlib.sha256).hexdigest().upper()
            return hashed

        # Add signature to params
        signature = generate_signature(params, app_secret, API_OPERATION)
        params['sign'] = signature
        
        # Display status
        status_attr = curses.color_pair(4) if has_colors else curses.A_NORMAL
        stdscr.addstr(current_y, 2, "Creating access token...", status_attr)
        stdscr.refresh()

        # Make the request
        headers = {
            'X-Protocol': 'GOP',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        # Make the POST request and ignore response
        requests.post(url, headers=headers, data=params)
        
        # Wait a moment for .env to be updated
        time.sleep(1)
        
        # Reload .env and check values
        load_dotenv()
        current_y += 2
        
        access_token = os.getenv('ACCESS_TOKEN')
        refresh_token = os.getenv('REFRESH_TOKEN')
        account = os.getenv('ACCOUNT')
        expires_at = os.getenv('EXPIRES_AT')
        
        if all([access_token, refresh_token, account, expires_at]):
            # Display success with values from .env
            success_attr = curses.color_pair(3) if has_colors else curses.A_NORMAL
            info_attr = curses.color_pair(4) if has_colors else curses.A_NORMAL
            
            stdscr.addstr(current_y, 2, "Access token created successfully!", success_attr)
            current_y += 2
            masked_token = mask_sensitive_data(access_token)
            stdscr.addstr(current_y, 2, f"Access Token: {masked_token}", info_attr)
            current_y += 1
            stdscr.addstr(current_y, 2, f"Account: {account}", info_attr)
            current_y += 1
            stdscr.addstr(current_y, 2, f"Expires at: {expires_at}", info_attr)
        else:
            error_attr = curses.color_pair(2) if has_colors else curses.A_NORMAL
            stdscr.addstr(current_y, 2, "Token creation status unclear, check .env file", error_attr)
    
    except Exception as e:
        current_y += 2
        try:
            error_attr = curses.color_pair(2) if has_colors else curses.A_NORMAL
            stdscr.addstr(current_y, 2, f"Error: {str(e)}", error_attr)
        except:
            pass
    
    # Final prompt
    try:
        current_y += 2
        prompt_attr = curses.color_pair(4) if has_colors else curses.A_NORMAL
        stdscr.addstr(current_y, 2, "Press any key to continue...", prompt_attr)
        stdscr.refresh()
        stdscr.getch()
    except:
        pass

def refresh_token(stdscr):
    # Clear screen and setup
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    current_y = 2
    has_colors = False
    
    try:
        # Initialize color pairs if supported
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(1, curses.COLOR_CYAN, -1)
            curses.init_pair(2, curses.COLOR_YELLOW, -1)
            curses.init_pair(3, curses.COLOR_GREEN, -1)
            curses.init_pair(4, curses.COLOR_BLUE, -1)
            has_colors = True
    except:
        pass
    
    try:
        # Load environment variables
        load_dotenv()
        app_key = os.getenv('APP_KEY')
        app_secret = os.getenv('APP_SECRET')
        refresh_token_val = os.getenv('REFRESH_TOKEN')
        
        # Check environment variables
        if not all([app_key, app_secret, refresh_token_val]):
            error_attr = curses.color_pair(2) if has_colors else curses.A_NORMAL
            stdscr.addstr(current_y, 2, "Error: Required environment variables missing in .env file", error_attr)
            current_y += 2
            stdscr.addstr(current_y, 2, "Please ensure APP_KEY, APP_SECRET, and REFRESH_TOKEN are set", error_attr)
            stdscr.refresh()
            stdscr.getch()
            return
        
        # API endpoint setup
        ALIBABA_SERVER_CALL_ENTRY = "https://openapi-api.alibaba.com/rest"
        API_OPERATION = "/auth/token/refresh"
        url = f"{ALIBABA_SERVER_CALL_ENTRY}{API_OPERATION}"

        # Generate timestamp
        timestamp = str(int(time.time() * 1000))

        # Prepare request parameters
        params = {
            "app_key": app_key,
            "refresh_token": refresh_token_val,
            "sign_method": "sha256",
            "timestamp": timestamp
        }

        # Generate signature
        def generate_signature(params, secret_key, api_operation):
            sorted_params = sorted(params.items())
            concatenated_string = api_operation
            for k, v in sorted_params:
                concatenated_string += f"{k}{v}"
            hashed = hmac.new(secret_key.encode('utf-8'), 
                            concatenated_string.encode('utf-8'), 
                            hashlib.sha256).hexdigest().upper()
            return hashed

        # Add signature to params
        signature = generate_signature(params, app_secret, API_OPERATION)
        params['sign'] = signature
        
        # Display status
        status_attr = curses.color_pair(4) if has_colors else curses.A_NORMAL
        stdscr.addstr(current_y, 2, "Refreshing access token...", status_attr)
        stdscr.refresh()

        # Make the request
        headers = {
            'X-Protocol': 'GOP',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        # Make the POST request and ignore response
        requests.post(url, headers=headers, data=params)
        
        # Wait a moment for .env to be updated
        time.sleep(1)
        
        # Reload .env and check values
        load_dotenv()
        current_y += 2
        
        # Check .env for updated values
        access_token = os.getenv('ACCESS_TOKEN')
        refresh_token = os.getenv('REFRESH_TOKEN')
        account = os.getenv('ACCOUNT')
        expires_at = os.getenv('EXPIRES_AT')
        
        if all([access_token, refresh_token, account, expires_at]):
            # Display success with values from .env
            success_attr = curses.color_pair(3) if has_colors else curses.A_NORMAL
            info_attr = curses.color_pair(4) if has_colors else curses.A_NORMAL
            
            stdscr.addstr(current_y, 2, "Token refreshed successfully!", success_attr)
            current_y += 2
            masked_token = mask_sensitive_data(access_token)
            stdscr.addstr(current_y, 2, f"New Access Token: {masked_token}", info_attr)
            current_y += 1
            stdscr.addstr(current_y, 2, f"Account: {account}", info_attr)
            current_y += 1
            stdscr.addstr(current_y, 2, f"Expires at: {expires_at}", info_attr)
        else:
            error_attr = curses.color_pair(2) if has_colors else curses.A_NORMAL
            stdscr.addstr(current_y, 2, "Token refresh status unclear, check .env file", error_attr)
    
    except Exception as e:
        current_y += 2
        try:
            error_attr = curses.color_pair(2) if has_colors else curses.A_NORMAL
            stdscr.addstr(current_y, 2, f"Error: {str(e)}", error_attr)
        except:
            pass
    
    # Final prompt
    try:
        current_y += 2
        prompt_attr = curses.color_pair(4) if has_colors else curses.A_NORMAL
        stdscr.addstr(current_y, 2, "Press any key to continue...", prompt_attr)
        stdscr.refresh()
        stdscr.getch()
    except:
        pass

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
    # Initialize curses
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)

    try:
        # Display splash screen
        display_splash_screen(stdscr)

        # Create main menu
        main_menu = Menu("Alibaba Open API CLI")

        # API Initialization and Authentication
        main_menu.add_item("Initialize API", "Set up API connection and get authorization code", initialize_api)
        main_menu.add_item("Create Token", "Generate access token using authorization code", create_token)
        main_menu.add_item("Refresh Token", "Refresh expired access token", refresh_token)

        # Product Management
        main_menu.add_item("Product Operations", "List, get, and manage products", display_product_list_usage)
        
        # Category Management
        main_menu.add_item("Category Operations", "Manage product categories", display_category_usage)
        
        # Inventory Management
        main_menu.add_item("Inventory Operations", "Manage product inventory", display_inventory_usage)
        
        # Photo Management
        main_menu.add_item("Photo Operations", "Manage product photos", display_photo_usage)

        # Schema Management
        main_menu.add_item("Schema Operations", "View and manage product schemas", lambda s: display_text_screen(s, "Schema Management API Usage", [
            "",
            ("Available Schema Endpoints:", 1),
            "",
            ("1. Get Schema:", 2),
            "   python product_schema_get.py --cat_id <category_id> [--schema_id <id>]",
            "",
            ("2. Add Schema:", 2),
            "   python product_schema_add.py --cat_id <category_id> --schema_file <path>",
            "",
            ("3. Update Schema:", 2),
            "   python product_schema_update.py --schema_id <id> --schema_file <path>",
            "",
            ("4. Add Schema Draft:", 2),
            "   python product_schema_add_draft.py --cat_id <category_id> --schema_file <path>",
            "",
            ("5. Get Schema Level:", 2),
            "   python product_schema_level_get.py <category_id>",
            "",
            ("6. Render Schema:", 2),
            "   python product_schema_render.py --schema_id <id> [--language <lang>]",
            "",
            ("7. Render Schema Draft:", 2),
            "   python product_schema_render_draft.py --draft_id <id> [--language <lang>]"
        ]))

        # Group Management
        main_menu.add_item("Group Operations", "Manage product groups", lambda s: display_text_screen(s, "Group Management API Usage", [
            "",
            ("Available Group Endpoints:", 1),
            "",
            ("1. Add Product to Group:", 2),
            "   python product_group_add.py --product_id <id> --group_id <id>"
        ]))

        # Product Utilities
        main_menu.add_item("Product Utilities", "Additional product operations", lambda s: display_text_screen(s, "Product Utilities API Usage", [
            "",
            ("Available Utility Endpoints:", 1),
            "",
            ("1. Check Product Availability:", 2),
            "   python product_available_get.py --product_id <id>",
            "",
            ("2. Get Product Score:", 2),
            "   python product_score_get.py --product_id <id>",
            "",
            ("3. Update Product Display Status:", 2),
            "   python product_update_display.py --product_id <id> --status <online|offline>",
            "",
            ("4. Encrypt/Decrypt Product ID:", 2),
            "   python product_id_encrypt.py --product_id <id> --convert_type <1|2>"
        ]))

        # Run the menu
        main_menu.run(stdscr)

        # Display exit screen
        display_exit_screen(stdscr)

    finally:
        # Clean up
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()

if __name__ == "__main__":
    main()
