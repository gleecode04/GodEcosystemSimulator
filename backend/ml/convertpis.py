import os
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

def find_county_column(df: pd.DataFrame, county_names: set) -> str:
    """Find the column that contains county names by matching values with known counties"""
    # List of common county column names
    county_column_names = ['County', 'COUNTY', 'LOCALECOUN', 'county', 'County Name']
    
    # First check for exact column name matches
    for col_name in county_column_names:
        if col_name in df.columns:
            values = set(str(x).upper().strip() for x in df[col_name].dropna().unique())
            matches = values.intersection(county_names)
            if len(matches) > 0:  # At least one valid county name found
                print(f"[INFO] Found {len(matches)} matching counties in '{col_name}' column")
                print(f"[INFO] Sample matches: {list(matches)[:5]}")
                return col_name
    
    # If no exact column match, look for columns with high percentage of county matches
    for col in df.columns:
        if col not in county_column_names:  # Skip already checked columns
            values = set(str(x).upper().strip() for x in df[col].dropna().unique())
            matches = values.intersection(county_names)
            
            # Calculate percentage of unique values that are valid counties
            if len(values) > 0:
                match_percentage = len(matches) / len(values) * 100
                
                # Only consider columns where at least 50% of unique values are valid counties
                if match_percentage >= 50 and len(matches) >= 3:
                    print(f"[INFO] Found column '{col}' with {len(matches)} county matches ({match_percentage:.1f}% of unique values)")
                    print(f"[INFO] Sample matches: {list(matches)[:5]}")
                    print(f"[INFO] Sample values: {list(values)[:10]}")
                    return col
            
    return None

def convert_to_fips(datasets_dir, fips_map_path, output_dir):
    """
    Converts county names to county numbers using california_counties.csv mapping.
    Only processes if county names are found in the data.
    """
    # Load FIPS mapping and create county names set
    fips_map = pd.read_csv(fips_map_path)
    fips_map['County Name'] = fips_map['County Name'].str.upper().str.strip()
    county_names = set(fips_map['County Name'])
    print(f"[INFO] Loaded {len(county_names)} county names from mapping file")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get list of all CSV files
    csv_files = [f for f in os.listdir(datasets_dir) if f.endswith('.csv') and f != 'california_counties.csv']
    print(f"\n[INFO] Found {len(csv_files)} CSV files to process")
    
    successful_files = []
    failed_files = []

    # Process each CSV file
    for file in csv_files:
        print(f"\n{'='*50}")
        print(f"[INFO] Processing {file}...")

        try:
            df = pd.read_csv(os.path.join(datasets_dir, file))
            print(f"[INFO] Shape: {df.shape}")
            print(f"[INFO] Columns: {df.columns.tolist()}")

            # Special handling for known datasets
            if file == "Oil_Spill_Incident_Tracking_[ds394].csv":
                county_column = "LOCALECOUN"
                print(f"[INFO] Using known county column '{county_column}' for oil spill dataset")
            else:
                county_column = find_county_column(df, county_names)

            if county_column:
                print(f"[SUCCESS] Found county column: {county_column}")
                
                # Prepare data for merge
                df['county_name'] = df[county_column].fillna('').str.upper().str.strip()
                
                # Print sample of data before merge
                print("\nSample of county names before merge:")
                print(df['county_name'].head())
                
                # Merge with FIPS mapping
                df_merged = df.merge(
                    fips_map[['County Name', 'County No.', 'Abbreviation']], 
                    left_on='county_name',
                    right_on='County Name',
                    how='left'
                )

                # Check merge results
                matched_counties = df_merged['County No.'].notna().sum()
                total_rows = len(df_merged)
                match_percentage = (matched_counties / total_rows * 100) if total_rows > 0 else 0
                
                print(f"\nMerge results:")
                print(f"Rows before merge: {len(df)}")
                print(f"Rows after merge: {len(df_merged)}")
                print(f"Matched counties: {matched_counties} ({match_percentage:.1f}%)")

                if matched_counties > 0:
                    print(f"[SUCCESS] Successfully mapped counties to numbers")
                    output_file = os.path.join(output_dir, file)
                    df_merged.to_csv(output_file, index=False)
                    print(f"[INFO] Saved processed file to {output_file}")
                    successful_files.append((file, f"{match_percentage:.1f}% matched"))
                else:
                    print("[WARNING] No counties were successfully mapped")
                    failed_files.append((file, "No successful mappings"))
            else:
                print("[WARNING] No column containing county names was found")
                failed_files.append((file, "No county column found"))

        except Exception as e:
            print(f"[ERROR] Failed to process file: {str(e)}")
            failed_files.append((file, str(e)))

    # Print summary
    print("\n" + "="*50)
    print("[SUMMARY]")
    print(f"Total files processed: {len(csv_files)}")
    print(f"Successfully processed: {len(successful_files)}")
    print(f"Failed to process: {len(failed_files)}")
    
    if successful_files:
        print("\nSuccessful files:")
        for file, match_info in successful_files:
            print(f"✅ {file} ({match_info})")
    
    if failed_files:
        print("\nFailed files:")
        for file, reason in failed_files:
            print(f"❌ {file}: {reason}")

if __name__ == "__main__":
    # Update paths to use the cloud_datasets directory
    datasets_dir = "./cloud_datasets"  # Changed from "./datasets" to "./cloud_datasets"
    fips_map_path = "./california_counties.csv"
    output_dir = "./processed_datasets"

    # Create directories if they don't exist
    for directory in [datasets_dir, output_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"[INFO] Created directory: {directory}")

    print("[INFO] Starting county number mapping...")
    convert_to_fips(datasets_dir, fips_map_path, output_dir)