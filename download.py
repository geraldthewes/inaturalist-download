import os
import logging
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
import pyarrow.parquet as pq
import requests
from typing import Dict, Any
from tqdm import tqdm
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def download_image(args: Dict[str, Any]) -> None:
    """
    Download image from URL and save it to the specified path.
    
    Args:
        args: Dictionary containing url, output_path
    """
    url = args['url']
    output_path = args['output_path']
    
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            logger.info(f"Successfully downloaded: {url}")
        else:
            logger.warning(f"Failed to download (HTTP {response.status_code}): {url}")
    except Exception as e:
        logger.error(f"Error downloading {url}: {str(e)}")

def main():
    parser = ArgumentParser(description='Download images from Parquet file')
    parser.add_argument('--parquet', type=str, required=True,
                       help='Path to the parquet file')
    parser.add_argument('--output', type=str, required=True,
                       help='Output directory where images will be stored')
    
    args = parser.parse_args()
    
    # Open Parquet file
    try:
        pf = pq.ParquetFile(args.parquet)
        num_row_groups = pf.num_row_groups
        print(f'Processing downloades in {num_row_groups} groups')
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            
            for rg_idx in range(num_row_groups):
                # Read row group
                print(f"Download group {rg_idx}/{num_row_groups}")
                batch = pf.read_row_group(rg_idx, columns=['id', 'identifier', 'foo', 'format'])
                
                # Convert to pandas DataFrame for easier processing
                df = batch.to_pandas()
                
                for _, row in tqdm(df.iterrows()):
                    if pd.isna(row['identifier']) or pd.isna(row['id']) or pd.isna(row['foo']):
                        continue

                    url = row['identifier']
                    identifier_id = str(row['id'])
                    foo_val = str(row['foo'])
                    file_format = row['format'].split('/')[-1] if '/' in row['format'] else row['format']

                    output_subdir = os.path.join(args.output, identifier_id)
                    filename = f"{foo_val}.{file_format}"
                    output_path = os.path.join(output_subdir, filename)

                    futures.append(executor.submit(
                        download_image,
                        {'url': url, 'output_path': output_path}
                    ))

            
            # Wait for all downloads to complete
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(str(e))
                    
    except Exception as e:
        logger.error(f"Error processing parquet file: {str(e)}")

if __name__ == "__main__":
    main()
