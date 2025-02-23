import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import geopandas as gpd
from shapely.geometry import Point
import json

class GeoDataMerger:
    def __init__(self):
        """Initialize the geo data merger"""
        self.county_data = None
        self.env_data = None
        self.geo_data = None
        
    def load_county_boundaries(self, geojson_path: str) -> None:
        """Load California county boundaries from GeoJSON"""
        try:
            self.county_data = gpd.read_file(geojson_path)
            print(f"Loaded {len(self.county_data)} county boundaries")
        except Exception as e:
            print(f"Error loading county boundaries: {str(e)}")
    
    def load_environmental_data(self, csv_path: str) -> None:
        """Load environmental data from CSV"""
        try:
            self.env_data = pd.read_csv(csv_path)
            print(f"Loaded environmental data with shape: {self.env_data.shape}")
        except Exception as e:
            print(f"Error loading environmental data: {str(e)}")
    
    def load_geographical_points(self, csv_path: str, lat_col: str, lon_col: str) -> None:
        """Load geographical point data"""
        try:
            df = pd.read_csv(csv_path)
            # Create GeoDataFrame from lat/lon
            geometry = [Point(xy) for xy in zip(df[lon_col], df[lat_col])]
            self.geo_data = gpd.GeoDataFrame(df, geometry=geometry)
            print(f"Loaded {len(self.geo_data)} geographical points")
        except Exception as e:
            print(f"Error loading geographical points: {str(e)}")
    
    def merge_data(self) -> Optional[gpd.GeoDataFrame]:
        """Merge all datasets based on spatial relationships"""
        try:
            if any(data is None for data in [self.county_data, self.env_data, self.geo_data]):
                print("Error: Not all required datasets are loaded")
                return None
            
            # First merge environmental data with county boundaries
            merged = self.county_data.merge(
                self.env_data,
                left_on='COUNTY_NAME',
                right_on='County Name',
                how='left'
            )
            
            # Spatial join with geographical points
            merged = gpd.sjoin(
                merged,
                self.geo_data,
                how='left',
                op='contains'
            )
            
            # Calculate additional metrics
            merged['point_density'] = merged.groupby('COUNTY_NAME')['index_right'].transform('count')
            merged['avg_elevation'] = merged.groupby('COUNTY_NAME')['elevation'].transform('mean')
            
            print(f"Successfully merged data with shape: {merged.shape}")
            return merged
            
        except Exception as e:
            print(f"Error merging data: {str(e)}")
            return None
    
    def calculate_spatial_metrics(self, merged_data: gpd.GeoDataFrame) -> Dict:
        """Calculate spatial metrics for environmental analysis"""
        try:
            metrics = {
                'county_metrics': {},
                'global_metrics': {
                    'total_counties': len(merged_data['COUNTY_NAME'].unique()),
                    'total_points': merged_data['point_density'].sum(),
                    'avg_elevation': merged_data['avg_elevation'].mean()
                }
            }
            
            # Calculate per-county metrics
            for county in merged_data['COUNTY_NAME'].unique():
                county_data = merged_data[merged_data['COUNTY_NAME'] == county]
                metrics['county_metrics'][county] = {
                    'point_density': float(county_data['point_density'].iloc[0]),
                    'avg_elevation': float(county_data['avg_elevation'].mean()),
                    'area_km2': float(county_data.geometry.area.iloc[0] / 1e6),  # Convert to km²
                    'environmental_score': float(county_data['Pollution Burden Score'].mean())
                }
            
            return metrics
            
        except Exception as e:
            print(f"Error calculating metrics: {str(e)}")
            return {}
    
    def save_results(self, merged_data: gpd.GeoDataFrame, output_path: str) -> None:
        """Save merged data and metrics"""
        try:
            # Save GeoJSON
            merged_data.to_file(f"{output_path}_merged.geojson", driver='GeoJSON')
            
            # Calculate and save metrics
            metrics = self.calculate_spatial_metrics(merged_data)
            with open(f"{output_path}_metrics.json", 'w') as f:
                json.dump(metrics, f, indent=2)
            
            print(f"Results saved to {output_path}_merged.geojson and {output_path}_metrics.json")
            
        except Exception as e:
            print(f"Error saving results: {str(e)}")

def main():
    # Initialize merger
    merger = GeoDataMerger()
    
    # Load data
    merger.load_county_boundaries("data/california_counties.geojson")
    merger.load_environmental_data("data/merged_california_data.csv")
    merger.load_geographical_points(
        "data/california_points.csv",
        lat_col="latitude",
        lon_col="longitude"
    )
    
    # Merge data
    merged_data = merger.merge_data()
    
    if merged_data is not None:
        # Save results
        merger.save_results(merged_data, "output/california_geo_env")

if __name__ == "__main__":
    main() 