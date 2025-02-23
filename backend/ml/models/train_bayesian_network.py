import pandas as pd
import numpy as np
from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.estimators import MaximumLikelihoodEstimator, BayesianEstimator
from sklearn.preprocessing import KBinsDiscretizer
import json
import os
import pickle
from scipy import stats
from sklearn.preprocessing import RobustScaler

def prepare_data():
    """Prepare data for Bayesian Network with enhanced preprocessing"""
    print("[INFO] Loading data...")
    df = pd.read_csv('../merged_california_data.csv')
    
    # Load our analysis to get categories
    with open('../dataset_analysis.json', 'r') as f:
        analysis = json.load(f)
    
    # Select key variables from each category
    key_variables = {
        'environmental_pressure': [
            'calenviroscreen_3.0_results_june_2018_update__Pollution Burden Score',
            'calenviroscreen_3.0_results_june_2018_update__Traffic',
            'calenviroscreen_3.0_results_june_2018_update__Pesticides',
            'calenviroscreen_3.0_results_june_2018_update__Diesel PM',
            'calenviroscreen_3.0_results_june_2018_update__Tox. Release'
        ],
        'environmental_state': [
            'calenviroscreen_3.0_results_june_2018_update__Ozone',
            'calenviroscreen_3.0_results_june_2018_update__PM2.5',
            'Species_Biodiversity___ACE_[ds2769]__SpBioRnkEco',
            'Species_Biodiversity___ACE_[ds2769]__TerrHabRank'
        ],
        'impact': [
            'calenviroscreen_3.0_results_june_2018_update__Asthma',
            'calenviroscreen_3.0_results_june_2018_update__Cardiovascular Disease',
            'calenviroscreen_3.0_results_june_2018_update__Low Birth Weight',
            'Terrestrial_Climate_Vulnerable_Species___ACE_[ds2701]__ClimVulVertCount'
        ]
    }
    
    print("[INFO] Preparing variables for network...")
    selected_columns = [col for category in key_variables.values() for col in category]
    data = df[selected_columns].copy()
    
    # Enhanced preprocessing
    discretized_data = pd.DataFrame()
    discretizers = {}
    
    def safe_iqr(x):
        """Calculate IQR safely handling NaN values"""
        q75, q25 = np.nanpercentile(x, [75, 25])
        return q75 - q25
    
    for col in data.columns:
        print(f"[INFO] Processing {col}")
        numeric_data = pd.to_numeric(data[col], errors='coerce')
        
        if numeric_data.notna().sum() > 0:
            # Fill NaN with median before processing
            median_val = numeric_data.median()
            numeric_data = numeric_data.fillna(median_val)
            
            # Outlier detection using IQR method
            Q1 = np.nanpercentile(numeric_data, 25)
            Q3 = np.nanpercentile(numeric_data, 75)
            IQR = Q3 - Q1
            if IQR == 0:  # Handle zero IQR case
                IQR = np.nanstd(numeric_data) or 1.0  # Use std dev or 1.0 if std dev is 0
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # Cap outliers instead of removing
            numeric_data = numeric_data.clip(lower_bound, upper_bound)
            
            # Robust scaling to handle remaining outliers
            scaler = RobustScaler(quantile_range=(25, 75))
            scaled_data = scaler.fit_transform(numeric_data.values.reshape(-1, 1))
            
            # Safe bin calculation
            n = len(scaled_data)
            iqr_val = safe_iqr(scaled_data)
            if iqr_val == 0:
                n_bins = 5  # Default to 5 bins if data is too uniform
            else:
                h = 2 * iqr_val / (n ** (1/3))  # bin width
                data_range = np.nanmax(scaled_data) - np.nanmin(scaled_data)
                if h == 0 or data_range == 0:
                    n_bins = 5  # Default for uniform data
                else:
                    n_bins = max(min(int(data_range / h), 10), 3)
            
            print(f"  Using {n_bins} bins for {col}")
            
            # Discretize using optimal bins
            discretizer = KBinsDiscretizer(
                n_bins=n_bins,
                encode='ordinal',
                strategy='quantile'  # More robust than 'uniform' for skewed data
            )
            discretized_values = discretizer.fit_transform(scaled_data).ravel()
            discretizers[col] = {
                'scaler': scaler,
                'discretizer': discretizer,
                'n_bins': n_bins
            }
            
        else:  # Handle categorical data
            # More sophisticated handling of categorical data
            filled_data = data[col].fillna(data[col].mode().iloc[0] if not data[col].mode().empty else "UNKNOWN")
            
            # Combine rare categories
            value_counts = filled_data.value_counts()
            rare_categories = value_counts[value_counts < len(filled_data) * 0.05].index
            filled_data = filled_data.replace(rare_categories, 'Other')
            
            categories = filled_data.unique()
            category_map = {cat: idx for idx, cat in enumerate(sorted(categories))}
            discretized_values = filled_data.map(category_map)
            discretizers[col] = {'type': 'categorical', 'mapping': category_map}
            
        discretized_data[col] = discretized_values
    
    print("\n[INFO] Variable Processing Summary:")
    for col in discretized_data.columns:
        unique_vals = len(discretized_data[col].unique())
        print(f"- {col}: {unique_vals} unique values")
        if col in discretizers and 'n_bins' in discretizers[col]:
            print(f"  Optimal bins: {discretizers[col]['n_bins']}")
    
    return discretized_data, key_variables, discretizers

def create_network(key_variables):
    """Define Bayesian Network structure based on domain knowledge"""
    print("[INFO] Creating network structure...")
    
    # Define edges based on causal relationships
    edges = []
    
    # Environmental Pressure -> Environmental State
    for pressure in key_variables['environmental_pressure']:
        for state in key_variables['environmental_state']:
            # Add edge for every pressure-state pair since they're all potentially related
            edges.append((pressure, state))
    
    # Environmental State -> Impact
    for state in key_variables['environmental_state']:
        for impact in key_variables['impact']:
            # Add edge for every state-impact pair since they're all potentially related
            edges.append((state, impact))
    
    # Environmental Pressure -> Impact (direct effects)
    for pressure in key_variables['environmental_pressure']:
        for impact in key_variables['impact']:
            # Add direct connections from pressures to impacts
            edges.append((pressure, impact))
    
    print(f"[INFO] Created {len(edges)} edges in network")
    model = BayesianNetwork(edges)
    return model

def train_network():
    """Train Bayesian Network"""
    # Prepare data
    data, key_variables, discretizers = prepare_data()
    
    # Create network
    model = create_network(key_variables)
    
    print("[INFO] Training network...")
    # Fit model using Bayesian estimation for better handling of sparse data
    model.fit(data=data, estimator=BayesianEstimator, prior_type='BDeu', equivalent_sample_size=10)
    
    # Save discretizers for later use
    print("[INFO] Saving model artifacts...")
    if not os.path.exists('../models'):
        os.makedirs('../models')
        
    with open('../models/bayesian_network.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    with open('../models/discretizers.pkl', 'wb') as f:
        pickle.dump(discretizers, f)
    
    with open('../models/key_variables.json', 'w') as f:
        json.dump(key_variables, f, indent=2)
    
    print("[SUCCESS] Model training complete")
    return model, discretizers, key_variables

if __name__ == "__main__":
    print("[INFO] Starting Bayesian Network training...")
    model, discretizers, key_variables = train_network() 