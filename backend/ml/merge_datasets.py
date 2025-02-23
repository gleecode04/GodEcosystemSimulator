import os
import pandas as pd
import numpy as np

def aggregate_by_county(df: pd.DataFrame, file_name: str) -> pd.DataFrame:
    """Aggregate data by county using appropriate methods for different columns"""
    print(f"[INFO] Aggregating {file_name} by county...")
    
    agg_dict = {}
    for col in df.columns:
        if col == 'County No.':
            continue
            
        # Sample the data to determine appropriate aggregation
        sample = df[col].head(100)
        
        try:
            # Try converting to numeric
            numeric_data = pd.to_numeric(sample)
            
            # If successful, use mean for numeric data
            agg_dict[col] = 'mean'
        except:
            # For non-numeric data, use most common value
            agg_dict[col] = lambda x: x.mode().iloc[0] if not x.empty else None
    
    # Perform aggregation
    aggregated = df.groupby('County No.').agg(agg_dict).reset_index()
    
    # Round numeric columns to 2 decimal places
    for col in aggregated.columns:
        if aggregated[col].dtype in ['float64', 'float32']:
            aggregated[col] = aggregated[col].round(2)
    
    print(f"[INFO] Reduced from {len(df)} to {len(aggregated)} rows")
    return aggregated

def merge_processed_datasets():
    """
    Merges all processed datasets from the processed_datasets directory
    using County No. as the key for joining.
    """
    processed_dir = "./processed_datasets"
    output_file = "merged_california_data.csv"
    
    # Get list of all processed CSV files
    csv_files = [f for f in os.listdir(processed_dir) if f.endswith('.csv')]
    print(f"[INFO] Found {len(csv_files)} processed files to merge")
    
    # Initialize empty list to store dataframes
    merged_df = None
    file_stats = []
    
    for file in csv_files:
        print(f"\n[INFO] Processing {file}...")
        try:
            # Read only necessary columns first to check for County No.
            columns = pd.read_csv(os.path.join(processed_dir, file), nrows=0).columns
            if 'County No.' not in columns:
                print(f"[SKIP] {file} does not contain County No. column")
                continue
            
            # Read the CSV file with optimized settings
            df = pd.read_csv(
                os.path.join(processed_dir, file),
                dtype={'County No.': 'float64'},
                low_memory=False
            )
            
            # Keep only the rows with valid county numbers
            df = df[df['County No.'].notna()]
            
            if len(df) == 0:
                print(f"[SKIP] {file} has no valid county data")
                continue
            
            # Get relevant columns (exclude common mapping columns we added)
            columns_to_exclude = ['county_name', 'County Name', 'Abbreviation']
            relevant_columns = [col for col in df.columns if col not in columns_to_exclude]
            df = df[relevant_columns]
            
            # Add file prefix to column names to avoid conflicts
            prefix = file.replace('.csv', '').replace(' ', '_').replace('-', '_')
            df.columns = [f"{prefix}__{col}" if col != 'County No.' else col for col in df.columns]
            
            # Aggregate data by county
            df = aggregate_by_county(df, file)
            
            # Convert to more memory-efficient types where possible
            for col in df.columns:
                if col != 'County No.':
                    if df[col].dtype == 'float64':
                        df[col] = df[col].astype('float32')
                    elif df[col].dtype == 'int64':
                        df[col] = df[col].astype('int32')
            
            # Merge with existing data
            if merged_df is None:
                merged_df = df
            else:
                # Merge only on County No. column
                merged_df = merged_df.merge(
                    df,
                    on='County No.',
                    how='outer',
                    validate='1:1'  # Ensure we don't accidentally duplicate rows
                )
            
            # Record statistics
            file_stats.append({
                'file': file,
                'columns_added': len(df.columns) - 1,  # subtract County No.
                'rows': len(df)
            })
            
            print(f"[SUCCESS] Added {len(df.columns) - 1} columns from {file}")
            print(f"Current merged shape: {merged_df.shape}")
            
        except Exception as e:
            print(f"[ERROR] Failed to process {file}: {str(e)}")
            import traceback
            print(traceback.format_exc())
    
    if merged_df is not None:
        try:
            # Save merged dataset
            print("\n[INFO] Saving merged dataset...")
            merged_df.to_csv(output_file, index=False)
            print(f"[SUCCESS] Saved merged dataset to {output_file}")
            print(f"Final shape: {merged_df.shape}")
            
            # Print summary
            print("\n[SUMMARY]")
            print("Files processed successfully:")
            for stat in file_stats:
                print(f"✅ {stat['file']}")
                print(f"   - Added {stat['columns_added']} columns")
                print(f"   - Contained {stat['rows']} county records")
        except Exception as e:
            print(f"[ERROR] Failed to save merged dataset: {str(e)}")
    else:
        print("\n[ERROR] No valid datasets were found to merge")

if __name__ == "__main__":
    print("[INFO] Starting dataset merge process...")
    merge_processed_datasets() 