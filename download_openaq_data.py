import boto3
import botocore
import os
from pathlib import Path
import gzip
import shutil
from openaq import OpenAQ

# S3 configuration
BUCKET = "openaq-data-archive"
REGION = "us-east-1"

# Create S3 client with anonymous access (equivalent to --no-sign-request)
s3 = boto3.client(
    's3',
    region_name=REGION,
    config=botocore.config.Config(signature_version=botocore.UNSIGNED)
)

# Fetch locations from OpenAQ API
print("Fetching location details from OpenAQ API...")
client = OpenAQ(api_key='40f7484413a58f2286d1abb283ba6a3ca0771e94f133e37952000b0391c2b324')
result = client.locations.list(coordinates=(5.651221, -0.185531), radius=12000, limit=1000)
client.close()

locations = result.results
location_map = {
    loc.id: (
        loc.locality if loc.locality else loc.name,  # location folder
        loc.owner.name if loc.owner else "Unknown",   # sensor type (owner) folder
        loc.provider.name if loc.provider else "Unknown"  # provider info (in data)
    )
    for loc in locations
}

print(f"Found {len(locations)} locations\n")

# Create data directory
data_dir = Path("openaq_data")
data_dir.mkdir(exist_ok=True)

def list_s3_objects(bucket, prefix):
    """List all objects with given prefix"""
    try:
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket, Prefix=prefix)
        
        objects = []
        for page in pages:
            if 'Contents' in page:
                objects.extend(page['Contents'])
        return objects
    except Exception as e:
        print(f"Error listing objects with prefix {prefix}: {e}")
        return []

def sanitize_filename(name):
    """Remove invalid filesystem characters"""
    invalid_chars = '<>:"|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name.strip()

def download_file(bucket, key, local_path):
    """Download a file from S3"""
    try:
        # Get filename without extension for decompressed version
        filename = Path(key).name
        print(f"  Downloading: {filename}")
        
        # Download to temporary gzipped file
        temp_gz_path = str(local_path) + '.gz_tmp'
        s3.download_file(bucket, key, temp_gz_path)
        
        # Decompress to final path
        try:
            with gzip.open(temp_gz_path, 'rb') as f_in:
                with open(local_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            # Remove temporary gzipped file
            os.remove(temp_gz_path)
        except Exception as decomp_error:
            print(f"    Error decompressing: {decomp_error}")
            # If decompression fails, keep the original file as-is
            if os.path.exists(temp_gz_path):
                os.rename(temp_gz_path, local_path)
        
        return True
    except Exception as e:
        print(f"  Error downloading {Path(key).name}: {e}")
        return False

print("=" * 70)
print("OpenAQ S3 Data Download - Organized by Sensor Type & Location")
print("=" * 70)

downloaded_count = 0
total_files = 0
failed_locations = []

# For each location, find and download all available data
for location_id, (location_name, owner_name, provider_name) in sorted(location_map.items()):
    # Sanitize folder name - owner is sensor type
    sensor_folder = sanitize_filename(owner_name)
    location_folder = sanitize_filename(location_name)
    
    # List all years available for this location
    prefix = f"records/csv.gz/locationid={location_id}/"
    print(f"\n{sensor_folder} > {location_folder} (ID: {location_id}, Provider: {provider_name}):")
    
    objects = list_s3_objects(BUCKET, prefix)
    
    if not objects:
        print(f"  No data found")
        continue
    
    # Group by year
    years = {}
    for obj in objects:
        key = obj['Key']
        if 'year=' in key:
            year = key.split('year=')[1].split('/')[0]
            if year not in years:
                years[year] = []
            years[year].append(key)
    
    print(f"  Available years: {sorted(years.keys())}")
    
    # Download all files for this location
    try:
        for year in sorted(years.keys()):
            year_dir = data_dir / sensor_folder / location_folder / f"year_{year}"
            year_dir.mkdir(parents=True, exist_ok=True)
            
            for key in years[year]:
                filename = Path(key).name
                # Remove .gz from filename if present
                if filename.endswith('.gz'):
                    filename = filename[:-3]
                
                local_file = year_dir / filename
                
                if not local_file.exists() or local_file.stat().st_size == 0:
                    if download_file(BUCKET, key, str(local_file)):
                        downloaded_count += 1
                else:
                    print(f"  File already exists: {filename}")
                
                total_files += 1
    except Exception as e:
        print(f"  Error processing location: {e}")
        failed_locations.append((location_id, location_name))

print("\n" + "=" * 70)
print(f"Download Complete!")
print(f"Downloaded: {downloaded_count} new files")
print(f"Total files processed: {total_files}")
print(f"Data location: {data_dir.absolute()}")
if failed_locations:
    print(f"Failed locations: {len(failed_locations)}")
    for lid, lname in failed_locations:
        print(f"  - {lname} (ID: {lid})")
print("=" * 70)
