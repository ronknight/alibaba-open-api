import json
import os
import csv
import argparse
from datetime import datetime
import subprocess

def get_product_details(product_id):
    """
    Get product details using product_get.py script
    
    Args:
        product_id (str): The product ID to get details for
        
    Returns:
        tuple: (model_number, sgm_sku) or (None, None) if failed
    """
    try:
        # Get the absolute path to product_get.py
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        product_get_script = os.path.join(base_dir, 'product_get.py')
        
        # Run the product_get.py script without saving JSON files
        process = subprocess.run(['python', product_get_script, '--product_id', str(product_id)], 
                               capture_output=True,
                               text=True,
                               check=True)
        
        # Check if there's any output in stderr
        if process.stderr and 'Warning' not in process.stderr:
            print(f"Warning for product {product_id}: {process.stderr}")
        
        # Parse the JSON response directly from stdout
        output_lines = process.stdout.strip().split('\n')
        for line in output_lines:
            try:
                data = json.loads(line)
                if isinstance(data, dict) and 'product' in data:
                    product = data.get('product', {})
                    model_number = ''
                    sgm_sku = ''
                    for attr in product.get('attributes', []):
                        if attr.get('attributeName', '').lower() == 'model number':
                            model_number = attr.get('valueName', '')
                        elif attr.get('attributeName', '').upper() == '4SGM_SKU':
                            sgm_sku = attr.get('valueName', '')
                    return model_number, sgm_sku
            except json.JSONDecodeError:
                continue
        
        print(f"No valid product data found for product {product_id}")
    except subprocess.CalledProcessError as e:
        print(f"Error running product_get.py for product {product_id}: {e}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
    except Exception as e:
        print(f"Error getting details for product {product_id}: {str(e)}")
    
    return None, None

def parse_product_info(json_file_path):
    """
    Parse product IDs and display values from a JSON file and fetch additional details.
    
    Args:
        json_file_path (str): Path to the JSON file containing product information
        
    Returns:
        list: List of tuples containing (product_id, display_value, model_number, sgm_sku)
    """
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
        
        products = data.get('products', [])
        product_info = []
        
        print("Fetching product details...")
        total_products = len(products)
        
        for idx, product in enumerate(products, 1):
            product_id = product.get('id', 'N/A')
            display = product.get('display', 'N/A')
            
            print(f"Processing product {idx}/{total_products} (ID: {product_id})")
            
            # Get additional details using product_get.py
            model_number, sgm_sku = get_product_details(product_id)
            
            product_info.append((product_id, display, model_number, sgm_sku))
        
        return product_info
            
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return []

def save_to_csv(product_info, output_dir='api_logs'):
    """
    Save the parsed product information to a CSV file.
    
    Args:
        product_info (list): List of tuples containing (product_id, display_value, model_number, sgm_sku)
        output_dir (str): Directory to save the CSV file
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_file = os.path.join(output_dir, f'product_info_{timestamp}.csv')
    
    try:
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Product ID', 'Display Value', 'Model Number', '4SGM_SKU'])
            writer.writerows(product_info)
        print(f"Product information saved to: {output_file}")
    
    except Exception as e:
        print(f"Error saving CSV file: {str(e)}")

def get_latest_json_file(api_logs_dir):
    """
    Get the path to the most recent all_products JSON file.
    
    Args:
        api_logs_dir (str): Directory containing the JSON files
        
    Returns:
        str: Path to the latest JSON file or None if no files found
    """
    json_files = [f for f in os.listdir(api_logs_dir) if f.startswith('all_products_') and f.endswith('.json')]
    if not json_files:
        return None
    latest_file = max(json_files)
    return os.path.join(api_logs_dir, latest_file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse product information from JSON file')
    parser.add_argument('--json-file', type=str, help='Path to the JSON file to parse (optional, uses latest if not provided)')
    args = parser.parse_args()
    
    # Get the absolute path to the api_logs directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    api_logs_dir = os.path.join(base_dir, 'api_logs')
    
    # Use provided JSON file or find the latest one
    if args.json_file:
        json_file_path = args.json_file
        if not os.path.exists(json_file_path):
            print(f"Error: File not found: {json_file_path}")
            exit(1)
    else:
        json_file_path = get_latest_json_file(api_logs_dir)
        if not json_file_path:
            print("No product JSON files found in api_logs directory")
            exit(1)
    
    # Parse the product information
    product_info = parse_product_info(json_file_path)
    
    if product_info:
        # Save to CSV
        save_to_csv(product_info, api_logs_dir)
    else:
        print("No product information found or error occurred while parsing")
