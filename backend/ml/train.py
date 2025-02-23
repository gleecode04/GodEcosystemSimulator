# backend/ml/train.py

import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient, ContainerClient

def get_blob_service_client():
    """Create and return a blob service client using connection string"""
    try:
        # Load environment variables from parent directory's .env
        load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
        connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        
        if not connect_str:
            raise ValueError("Azure Storage connection string not found in environment variables")
            
        return BlobServiceClient.from_connection_string(connect_str)
    except Exception as e:
        print(f"[ERROR] Failed to create blob service client: {str(e)}")
        raise

def download_and_read_csv(container_name: str, blob_name: str) -> pd.DataFrame:
    """Download a CSV file from Azure Blob Storage and read it into a pandas DataFrame"""
    try:
        print(f"[INFO] Attempting to download {blob_name} from container {container_name}")
        
        # Get blob service client
        blob_service_client = get_blob_service_client()
        
        # Get container client
        container_client = blob_service_client.get_container_client(container_name)
        
        # Get blob client
        blob_client = container_client.get_blob_client(blob_name)
        
        # Download blob content
        download_stream = blob_client.download_blob()
        
        # Read directly into pandas
        df = pd.read_csv(download_stream)
        
        print(f"[INFO] Successfully downloaded and read {blob_name}")
        return df
        
    except Exception as e:
        print(f"[ERROR] Failed to download and read blob: {str(e)}")
        raise

def main():
    try:
        # Specify container and blob names
        container_name = "datasets"
        blob_name = "Vegetation_-_Garrapata_State_Park_[ds2945].csv"
        
        # Download and read the CSV
        df = download_and_read_csv(container_name, blob_name)
        
        # Print information about the dataset
        print("\n[INFO] Dataset Information:")
        print("Shape:", df.shape)
        print("\nColumns:", df.columns.tolist())
        print("\nFirst few rows:")
        print(df.head())
        print("\nBasic statistics:")
        print(df.describe())
        
    except Exception as e:
        print(f"[ERROR] Failed in main: {str(e)}")
        raise

if __name__ == "__main__":
    main()
