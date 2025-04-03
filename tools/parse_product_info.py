import json
import os
import csv
import argparse
from datetime import datetime

def parse_product_info(json_file_path):
    """
    Parse product IDs and display values from a JSON file.
    
    Args:
        json_file_path (str): Path to the JSON file containing product information
        
    Returns:
        list: List of tuples containing (product_id, display_value)
    """
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            
        products = data.get('products', [])
        product_info = []
        
        for product in products:
            product_id = product.get('id', 'N/A')
            display = product.get('display', 'N/A')
            product_info.append((product_id, display))
            
        return product_info
    
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return []

def save_to_csv(product_info, output_dir='api_logs'):
    """
    Save the parsed product information to a CSV file.
    
    Args:
        product_info (list): List of tuples containing (product_id, display_value)
        output_dir (str): Directory to save the CSV file
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_file = os.path.join(output_dir, f'product_info_{timestamp}.csv')
    
    try:
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Product ID', 'Display Value'])
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