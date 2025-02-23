import pandas as pd
import numpy as np
import json

def get_numeric_stats(series):
    """Calculate statistics for numeric columns"""
    try:
        return {
            'mean': float(series.mean()),
            'std': float(series.std()),
            'min': float(series.min()),
            'max': float(series.max()),
            'missing': int(series.isna().sum()),
            'type': str(series.dtype)
        }
    except:
        return None

def get_categorical_stats(series):
    """Calculate statistics for categorical columns"""
    try:
        return {
            'unique_values': series.nunique(),
            'most_common': series.mode().iloc[0] if not series.mode().empty else None,
            'missing': int(series.isna().sum()),
            'type': str(series.dtype)
        }
    except:
        return None

def categorize_variable(col_name: str) -> str:
    """Categorize variables more precisely"""
    col_lower = col_name.lower()
    
    # Environmental Input Variables
    if any(term in col_lower for term in [
        'pollution', 'emission', 'traffic', 'waste', 'pesticides', 
        'toxic', 'diesel', 'cleanup', 'hazardous'
    ]):
        return 'environmental_pressure'
        
    # Environmental State Variables
    elif any(term in col_lower for term in [
        'water_quality', 'air_quality', 'ozone', 'pm2.5',
        'biodiversity', 'species', 'habitat', 'aquatic',
        'groundwater', 'drinking_water'
    ]):
        return 'environmental_state'
        
    # Impact Variables
    elif any(term in col_lower for term in [
        'health', 'asthma', 'cardiovascular', 'birth_weight',
        'disease', 'poverty', 'education', 'unemployment'
    ]):
        return 'impact'
        
    # Response Variables
    elif any(term in col_lower for term in [
        'protection', 'conservation', 'restoration',
        'mitigation', 'management', 'policy'
    ]):
        return 'response'
        
    # Metadata/Context
    else:
        return 'metadata'

def analyze_dataset():
    """Analyze the merged dataset and categorize variables"""
    print("[INFO] Loading merged dataset...")
    df = pd.read_csv('merged_california_data.csv')
    
    # Analyze each column
    analysis = {}
    for col in df.columns:
        if col == 'County No.':
            continue
            
        print(f"[INFO] Analyzing column: {col}")
        
        # Try numeric stats first
        numeric_stats = get_numeric_stats(pd.to_numeric(df[col], errors='coerce'))
        
        if numeric_stats:
            stats = numeric_stats
            data_type = 'numeric'
        else:
            stats = get_categorical_stats(df[col])
            data_type = 'categorical'
        
        # Identify category (environmental input vs output)
        category = categorize_variable(col)
        
        # Store column analysis
        analysis[col] = {
            'stats': stats,
            'category': category,
            'data_type': data_type
        }
    
    # Save analysis
    print("\n[INFO] Saving analysis...")
    with open('dataset_analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2)
    
    # Print summary
    print("\n[SUMMARY]")
    print(f"Total features: {len(analysis)}")
    
    # Count by category
    categories = {cat: sum(1 for v in analysis.values() if v['category'] == cat) for cat in set(v['category'] for v in analysis.values())}
    print("\nCategories:")
    for cat, count in categories.items():
        print(f"- {cat}: {count}")
    
    # Count by data type
    numeric = sum(1 for v in analysis.values() if v['data_type'] == 'numeric')
    categorical = sum(1 for v in analysis.values() if v['data_type'] == 'categorical')
    print("\nData Types:")
    print(f"- Numeric variables: {numeric}")
    print(f"- Categorical variables: {categorical}")
    
    # Print some example features
    print("\nExample Input Features:")
    for col, info in analysis.items():
        if info['category'] in ['environmental_pressure', 'environmental_state', 'impact']:
            print(f"- {col}")
            break
            
    print("\nExample Output Features:")
    for col, info in analysis.items():
        if info['category'] in ['response', 'metadata']:
            print(f"- {col}")
            break

if __name__ == "__main__":
    print("[INFO] Starting dataset analysis...")
    analyze_dataset() 