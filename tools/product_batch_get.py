import os
import sys
import csv
import time
from datetime import datetime

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from product_get import fetch_product_details
from utils.terminal_colors import print_success, print_error, print_info, print_header

def process_products_from_csv(csv_file_path):
    # Read environment variables
    APP_KEY = os.getenv('APP_KEY')
    APP_SECRET = os.getenv('APP_SECRET')
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

    if not all([APP_KEY, APP_SECRET, ACCESS_TOKEN]):
        print_error("Missing required environment variables")
        return

    # Create output CSV path with timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_dir = "api_logs"
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.splitext(os.path.basename(csv_file_path))[0]
    output_csv_path = os.path.join(output_dir, f"{filename}_with_details_{timestamp}.csv")

    # Keep track of processing stats
    total_processed = 0
    successful = 0
    failed = 0
    
    # Read input CSV and create output CSV
    with open(csv_file_path, 'r') as infile, open(output_csv_path, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['redModel', '4SGM_SKU']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        total_rows = sum(1 for row in infile) - 1  # Subtract header row
        infile.seek(0)
        next(reader)  # Skip header row again
        
        print_header(f"\n=== Processing {total_rows} products ===")
        
        for i, row in enumerate(reader, 1):
            product_id = row['Product ID']
            print_info(f"\nProcessing product {i}/{total_rows}: {product_id}")
            
            try:
                # Fetch product details
                response_data = fetch_product_details(product_id, APP_KEY, APP_SECRET, ACCESS_TOKEN)
                
                if response_data and isinstance(response_data, dict):
                    product = None
                    # Handle both direct product response and nested response
                    if 'product' in response_data:
                        product = response_data['product']
                    elif 'response' in response_data and 'product' in response_data['response']:
                        product = response_data['response']['product']
                    
                    if product:
                        red_model = product.get('redModel', '')
                        
                        # Find 4SGM_SKU in attributes
                        sgm_sku = ''
                        if 'attributes' in product:
                            for attr in product['attributes']:
                                if attr.get('attributeName') == '4SGM_SKU':
                                    sgm_sku = attr.get('valueName', '')
                                    break
                        
                        # Update row with new data
                        row['redModel'] = red_model
                        row['4SGM_SKU'] = sgm_sku
                        
                        successful += 1
                        print_success(f"Successfully processed product {product_id}")
                        print_info(f"redModel: {red_model}")
                        print_info(f"4SGM_SKU: {sgm_sku}")
                    else:
                        row['redModel'] = ''
                        row['4SGM_SKU'] = ''
                        failed += 1
                        print_error(f"Failed to process product {product_id}: No product data found")
                else:
                    row['redModel'] = ''
                    row['4SGM_SKU'] = ''
                    failed += 1
                    print_error(f"Failed to process product {product_id}: Invalid response format")
                
            except Exception as e:
                row['redModel'] = ''
                row['4SGM_SKU'] = ''
                failed += 1
                print_error(f"Error processing product {product_id}: {str(e)}")
            
            # Write the row immediately after processing
            writer.writerow(row)
            total_processed += 1
            
            # Sleep for 1 seconds between requests (unless it's the last item)
            if i < total_rows:
                print_info("Waiting 1 seconds before next request...")
                time.sleep(1)
    
    print_success(f"\nProcessing complete!")
    print_info(f"Total processed: {total_processed}")
    print_success(f"Successful: {successful}")
    print_error(f"Failed: {failed}")
    print_info(f"Results saved to {output_csv_path}")
    
    return output_csv_path

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Process products from CSV file and extract redModel and 4SGM_SKU')
    parser.add_argument('csv_file', help='Path to the CSV file containing product IDs')
    args = parser.parse_args()
    
    process_products_from_csv(args.csv_file)

if __name__ == "__main__":
    main()