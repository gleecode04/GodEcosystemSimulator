import json
import pickle
from pgmpy.models import BayesianNetwork
from pgmpy.inference import VariableElimination
import numpy as np

class EnvironmentSimulator:
    def __init__(self):
        """Load the trained model and preprocessing artifacts"""
        # Load model and artifacts
        with open('bayesian_network.pkl', 'rb') as f:
            self.model = pickle.load(f)
        
        with open('discretizers.pkl', 'rb') as f:
            self.discretizers = pickle.load(f)
            
        with open('key_variables.json', 'r') as f:
            self.key_variables = json.load(f)
            
        # Initialize inference engine
        self.inference = VariableElimination(self.model)
        
    def _discretize_input(self, variable, value):
        """Convert continuous input to discrete states with enhanced preprocessing"""
        discretizer = self.discretizers[variable]
        if isinstance(discretizer, dict):
            if 'type' in discretizer:  # Categorical variable
                return discretizer['mapping'].get(value, 0)
            else:  # Numeric variable with enhanced preprocessing
                # Apply the same preprocessing as during training
                scaled_value = discretizer['scaler'].transform([[value]])[0][0]
                return int(discretizer['discretizer'].transform([[scaled_value]])[0])
        return 0  # Default case
    
    def _continuous_output(self, variable, state):
        """Convert discrete states back to continuous values with inverse preprocessing"""
        discretizer = self.discretizers[variable]
        if isinstance(discretizer, dict):
            if 'type' in discretizer:  # Categorical variable
                reverse_map = {v: k for k, v in discretizer['mapping'].items()}
                return reverse_map.get(state, "UNKNOWN")
            else:  # Numeric variable with enhanced preprocessing
                # Inverse transform through both discretizer and scaler
                continuous_scaled = discretizer['discretizer'].inverse_transform([[state]])[0][0]
                return float(discretizer['scaler'].inverse_transform([[continuous_scaled]])[0])
        return 0  # Default case

    def process_llm_input(self, text_input):
        """Convert LLM text output to model inputs
        Example input: "Reduce air pollution by 20% and increase green spaces by 15%"
        """
        # This would be replaced with actual LLM processing
        changes = {
            'calenviroscreen_3.0_results_june_2018_update__Pollution Burden Score': -20,
            'calenviroscreen_3.0_results_june_2018_update__Traffic': -15
        }
        return changes

    def simulate_changes(self, changes):
        """Simulate environmental changes with enhanced error handling"""
        try:
            # Convert inputs to discrete states
            evidence = {}
            for var, change in changes.items():
                if var not in self.discretizers:
                    print(f"Warning: Variable {var} not found in model")
                    continue
                    
                current_value = 50  # Default baseline
                new_value = current_value + change
                
                # Ensure value is within reasonable bounds
                new_value = max(0, min(100, new_value))  # Clip to 0-100 range
                
                evidence[var] = self._discretize_input(var, new_value)
            
            if not evidence:
                raise ValueError("No valid changes to simulate")
            
            # Predict impacts
            impacts = {}
            for impact_var in self.key_variables['impact']:
                try:
                    prediction = self.inference.query(variables=[impact_var], evidence=evidence)
                    most_likely_state = np.argmax(prediction.values)
                    impacts[impact_var] = self._continuous_output(impact_var, most_likely_state)
                except Exception as e:
                    print(f"Warning: Failed to predict {impact_var}: {str(e)}")
                    impacts[impact_var] = None
            
            return impacts
            
        except Exception as e:
            print(f"Error in simulation: {str(e)}")
            return {}

    def get_feature_importance(self):
        """Get importance scores for different features"""
        # Use model structure to determine feature importance
        importance = {}
        for var in self.model.nodes():
            importance[var] = len(self.model.get_children(var))
        return importance 