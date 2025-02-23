import os
import json
import pandas as pd
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

def main():
    """
    1. Connect to Azure Blob Storage (using .env).
    2. List all files in the 'datasets' container.
    3. For each CSV file, download into a DataFrame.
    4. Save analysis results to a JSON file.
    """
    try:
        # === 1. Load environment & connect to blob service ===
        load_dotenv()  # Make sure .env has AZURE_STORAGE_CONNECTION_STRING
        conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        if not conn_str:
            raise ValueError("AZURE_STORAGE_CONNECTION_STRING not found in .env")

        blob_service_client = BlobServiceClient.from_connection_string(conn_str)
        container_name = "datasets"
        container_client = blob_service_client.get_container_client(container_name)

        print(f"[INFO] Listing blobs in container: '{container_name}'...")

        # Initialize a dictionary to store all dataset analyses
        analysis_results = {}

        # === 2. Loop through all blobs ===
        blob_list = container_client.list_blobs()
        for blob in blob_list:
            blob_name = blob.name

            # Only process CSV files (skip images, text, etc.)
            if not blob_name.lower().endswith(".csv"):
                continue

            print(f"\n[INFO] Found CSV: {blob_name}. Downloading...")

            # === 3. Download the CSV into a pandas DataFrame ===
            blob_client = container_client.get_blob_client(blob_name)
            download_stream = blob_client.download_blob()
            try:
                df = pd.read_csv(download_stream)
            except Exception as e:
                analysis_results[blob_name] = {
                    "error": f"Could not read file as CSV: {str(e)}"
                }
                continue

            # === 4. Collect dataset information ===
            dataset_info = {
                "shape": {
                    "rows": df.shape[0],
                    "columns": df.shape[1]
                },
                "columns": list(df.columns),
                "sample_data": df.head(3).to_dict(orient='records'),
                "column_types": df.dtypes.astype(str).to_dict(),
                "correlation": None
            }

            # Add correlation matrix if possible
            numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
            if len(numeric_cols) > 1:
                corr_matrix = df[numeric_cols].corr()
                dataset_info["correlation"] = corr_matrix.to_dict()

            # Add basic statistics for numeric columns
            dataset_info["numeric_stats"] = df[numeric_cols].describe().to_dict() if len(numeric_cols) > 0 else None

            # Store results for this dataset
            analysis_results[blob_name] = dataset_info

        # === 5. Save analysis results to file ===
        output_file = "dataset_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(analysis_results, f, indent=2)

    except Exception as e:
        with open("analysis_error.txt", 'w') as f:
            f.write(str(e))

if __name__ == "__main__":
    main()
