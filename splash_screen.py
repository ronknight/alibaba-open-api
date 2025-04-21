import tkinter as tk
from tkinter import ttk, messagebox
import os
from dotenv import load_dotenv
import webbrowser
from urllib.parse import urlparse, parse_qs
import glob

class AlibabaSplashScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Alibaba Open API Interface")
        self.root.geometry("800x600")
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Initialize variables
        self.auth_code = tk.StringVar()
        self.selected_endpoint = tk.StringVar()
        
        # Create UI elements
        self.create_header()
        self.create_auth_section()
        self.create_endpoint_section()
        
    def create_header(self):
        header = ttk.Label(
            self.main_frame,
            text="Welcome to Alibaba Open API Interface",
            font=("Helvetica", 16, "bold")
        )
        header.grid(row=0, column=0, columnspan=2, pady=20)
        
    def create_auth_section(self):
        auth_frame = ttk.LabelFrame(self.main_frame, text="Authentication", padding="10")
        auth_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(
            auth_frame,
            text="1. Initialize API Connection",
            command=self.initialize_api
        ).grid(row=0, column=0, pady=5)
        
        ttk.Button(
            auth_frame,
            text="2. Create Access Token",
            command=self.create_token
        ).grid(row=1, column=0, pady=5)
        
        ttk.Button(
            auth_frame,
            text="3. Refresh Token",
            command=self.refresh_token
        ).grid(row=2, column=0, pady=5)
        
    def create_endpoint_section(self):
        endpoint_frame = ttk.LabelFrame(self.main_frame, text="Available Endpoints", padding="10")
        endpoint_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Get all Python files that represent endpoints
        endpoints = self.get_available_endpoints()
        
        # Create a listbox for endpoints
        self.endpoint_listbox = tk.Listbox(endpoint_frame, height=10, width=50)
        self.endpoint_listbox.grid(row=0, column=0, pady=5)
        
        # Add endpoints to listbox
        for endpoint in endpoints:
            self.endpoint_listbox.insert(tk.END, endpoint)
        
        ttk.Button(
            endpoint_frame,
            text="Run Selected Endpoint",
            command=self.run_selected_endpoint
        ).grid(row=1, column=0, pady=5)
        
    def get_available_endpoints(self):
        # Get all Python files in the root directory that might be endpoints
        files = glob.glob("*.py")
        endpoints = []
        
        # Filter out utility files and main interface files
        exclude_files = {'1initiate.py', '2createtoken.py', '3refreshtoken.py', 'splash_screen.py'}
        for file in files:
            if file not in exclude_files and file.endswith('.py'):
                # Remove .py extension and convert to readable format
                endpoint_name = file[:-3].replace('_', ' ').title()
                endpoints.append(f"{endpoint_name} ({file})")
                
        return sorted(endpoints)
        
    def initialize_api(self):
        try:
            import importlib
            initiate = importlib.import_module('1initiate')
            webbrowser.open(initiate.auth_url)
            
            # Get authorization code from user
            auth_code = tk.simpledialog.askstring(
                "Authorization Code",
                "Please enter the authorization code from the redirected URL:"
            )
            
            if auth_code:
                self.auth_code.set(auth_code)
                messagebox.showinfo("Success", "API initialized successfully!")
            else:
                messagebox.showerror("Error", "Authorization code is required!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize API: {str(e)}")
            
    def create_token(self):
        try:
            if not self.auth_code.get():
                messagebox.showerror("Error", "Please initialize the API first!")
                return
                
            import importlib
            create_token = importlib.import_module('2createtoken')
            messagebox.showinfo("Success", "Token created successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create token: {str(e)}")
            
    def refresh_token(self):
        try:
            import importlib
            refresh_token = importlib.import_module('3refreshtoken')
            messagebox.showinfo("Success", "Token refreshed successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh token: {str(e)}")
            
    def run_selected_endpoint(self):
        selection = self.endpoint_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select an endpoint to run!")
            return
            
        selected_item = self.endpoint_listbox.get(selection[0])
        filename = selected_item.split('(')[1].rstrip(')')
        
        try:
            import importlib
            endpoint_module = importlib.import_module(filename[:-3])
            messagebox.showinfo("Success", f"Running endpoint: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run endpoint: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AlibabaSplashScreen(root)
    root.mainloop()
