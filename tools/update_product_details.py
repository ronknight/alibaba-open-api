import csv
import os
import subprocess
import json
from datetime import datetime

def read_product_ids(csv_file):
    """Read product IDs from the CSV file"""
    product_ids = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            product_ids.append(row['Product ID'])
    return product_ids

def get_product_details(product_id):
    """Get product details using product_get.py"""
    try:
        cmd = f'python product_get.py --product_id {product_id}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        # Find the most recent response file for this product
        api_logs_dir = 'api_logs'
        response_files = [f for f in os.listdir(api_logs_dir) 
                         if f.startswith(f'product_response_{product_id}_') 
                         and f.endswith('.json')]
        
        if not response_files:
            return None, None
            
        latest_file = max(response_files)
        response_path = os.path.join(api_logs_dir, latest_file)
        
        with open(response_path, 'r') as f:
            data = json.load(f)
            
        product = data['response']['product']
        red_model = product.get('redModel', '')
        
        # Find 4SGM_SKU in attributes
        sgm_sku = ''
        for attr in product.get('attributes', []):
            if attr.get('attributeName') == '4SGM_SKU':
                sgm_sku = attr.get('valueName', '')
                break
                
        return red_model, sgm_sku
        
    except Exception as e:
        print(f"Error getting details for product {product_id}: {str(e)}")
        return None, None

def update_csv_with_details(input_csv):
    """Update CSV with product details"""
    # Read existing data
    rows = []
    with open(input_csv, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Update each row with new details
    total = len(rows)
    for i, row in enumerate(rows, 1):
        print(f"Processing {i}/{total}: Product ID {row['Product ID']}")
        red_model, sgm_sku = get_product_details(row['Product ID'])
        if red_model is not None:
            row['redModel'] = red_model
        if sgm_sku is not None:
            row['4SGM_SKU'] = sgm_sku
    
    # Save updated data to new file
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_file = os.path.join('api_logs', f'product_info_updated_{timestamp}.csv')
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"\nUpdated information saved to: {output_file}")

if __name__ == '__main__':
    # Get the latest product info CSV file
    api_logs_dir = 'api_logs'
    csv_files = [f for f in os.listdir(api_logs_dir) 
                 if f.startswith('product_info_') 
                 and f.endswith('.csv')]
    
    if not csv_files:
        print("No product info CSV files found")
        exit(1)
        
    latest_csv = max(csv_files)
    input_csv = os.path.join(api_logs_dir, latest_csv)
    
    print(f"Processing file: {input_csv}")
    update_csv_with_details(input_csv)
