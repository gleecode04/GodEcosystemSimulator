import numpy as np
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import KFold
import json
import pandas as pd
from inference import EnvironmentSimulator
import matplotlib.pyplot as plt
import seaborn as sns

class ModelEvaluator:
    def __init__(self, simulator: EnvironmentSimulator):
        self.simulator = simulator
        self.data = pd.read_csv('../merged_california_data.csv')
        
    def evaluate_predictive_accuracy(self, k_folds=5):
        """Evaluate model's predictive accuracy using k-fold cross validation"""
        print("[INFO] Evaluating predictive accuracy...")
        
        # Get pressure and impact variables
        pressure_vars = self.simulator.key_variables['environmental_pressure']
        impact_vars = self.simulator.key_variables['impact']
        
        results = {
            'mse': [],
            'r2': [],
            'fold_predictions': []
        }
        
        kf = KFold(n_splits=k_folds, shuffle=True, random_state=42)
        
        for fold, (train_idx, test_idx) in enumerate(kf.split(self.data)):
            print(f"\nFold {fold + 1}/{k_folds}")
            
            # Train model on training data
            train_data = self.data.iloc[train_idx]
            test_data = self.data.iloc[test_idx]
            
            # Make predictions
            fold_predictions = []
            for idx in test_idx:
                try:
                    # Get actual changes in pressure variables
                    changes = {var: float(self.data.iloc[idx][var]) for var in pressure_vars}
                    
                    # Skip if any pressure variables are missing
                    if any(np.isnan(val) for val in changes.values()):
                        continue
                    
                    # Predict impacts
                    predicted_impacts = self.simulator.simulate_changes(changes)
                    actual_impacts = {var: float(self.data.iloc[idx][var]) for var in impact_vars}
                    
                    # Skip if any actual impacts are missing
                    if any(np.isnan(val) for val in actual_impacts.values()):
                        continue
                    
                    fold_predictions.append({
                        'predicted': predicted_impacts,
                        'actual': actual_impacts
                    })
                except Exception as e:
                    print(f"[WARNING] Skipping sample due to error: {str(e)}")
                    continue
            
            if not fold_predictions:
                print("[WARNING] No valid predictions in this fold")
                continue
            
            # Calculate metrics
            try:
                mse = np.mean([
                    mean_squared_error(
                        list(pred['actual'].values()),
                        list(pred['predicted'].values())
                    )
                    for pred in fold_predictions
                ])
                
                r2 = np.mean([
                    r2_score(
                        list(pred['actual'].values()),
                        list(pred['predicted'].values())
                    )
                    for pred in fold_predictions
                ])
                
                results['mse'].append(mse)
                results['r2'].append(r2)
                results['fold_predictions'].append(fold_predictions)
                
                print(f"MSE: {mse:.4f}")
                print(f"R2 Score: {r2:.4f}")
                print(f"Valid predictions: {len(fold_predictions)}")
            except Exception as e:
                print(f"[WARNING] Could not calculate metrics for fold: {str(e)}")
                continue
        
        if not results['mse']:
            print("[WARNING] No valid results across any folds")
            return None
        
        return results
    
    def evaluate_causal_consistency(self):
        """Evaluate if the model's predictions follow expected causal relationships"""
        print("\n[INFO] Evaluating causal consistency...")
        
        # Test cases with known causal relationships
        test_cases = [
            {
                'changes': {
                    'calenviroscreen_3.0_results_june_2018_update__Pollution Burden Score': 20,
                    'calenviroscreen_3.0_results_june_2018_update__Traffic': 15
                },
                'expected_direction': {
                    'calenviroscreen_3.0_results_june_2018_update__Asthma': 'increase',
                    'calenviroscreen_3.0_results_june_2018_update__Cardiovascular Disease': 'increase'
                }
            },
            # Add more test cases...
        ]
        
        results = []
        for case in test_cases:
            impacts = self.simulator.simulate_changes(case['changes'])
            
            # Check if predictions follow expected directions
            for impact_var, expected in case['expected_direction'].items():
                actual_direction = 'increase' if impacts[impact_var] > 50 else 'decrease'
                consistent = actual_direction == expected
                
                results.append({
                    'case': case['changes'],
                    'impact_var': impact_var,
                    'expected': expected,
                    'actual': actual_direction,
                    'consistent': consistent
                })
        
        return results
    
    def evaluate_uncertainty(self):
        """Evaluate model's uncertainty estimates"""
        print("\n[INFO] Evaluating prediction uncertainty...")
        
        # Sample different input scenarios using actual variable names
        scenarios = [
            {
                'calenviroscreen_3.0_results_june_2018_update__Pollution Burden Score': -20,
                'calenviroscreen_3.0_results_june_2018_update__Traffic': -15
            },
            {
                'calenviroscreen_3.0_results_june_2018_update__Pollution Burden Score': 10,
                'calenviroscreen_3.0_results_june_2018_update__Traffic': 5
            },
            {
                'calenviroscreen_3.0_results_june_2018_update__Pollution Burden Score': 0,
                'calenviroscreen_3.0_results_june_2018_update__Traffic': 0
            }
        ]
        
        uncertainty_results = []
        for scenario in scenarios:
            # Make multiple predictions with small variations
            predictions = []
            for _ in range(100):
                # Add small random noise to inputs
                noisy_scenario = {
                    k: v + np.random.normal(0, 2) 
                    for k, v in scenario.items()
                }
                impacts = self.simulator.simulate_changes(noisy_scenario)
                predictions.append(impacts)
            
            # Calculate variance of predictions
            variances = {
                var: np.var([pred[var] for pred in predictions])
                for var in predictions[0].keys()
            }
            
            uncertainty_results.append({
                'scenario': scenario,
                'prediction_variance': variances
            })
        
        return uncertainty_results
    
    def evaluate_semantic_reliability(self, test_prompts):
        """Evaluate consistency of LLM interpretations"""
        print("\n[INFO] Evaluating semantic reliability...")
        
        results = []
        for prompt in test_prompts:
            # Get multiple interpretations
            interpretations = []
            for _ in range(5):  # Test multiple times
                changes = self.simulator.process_llm_input(prompt)
                interpretations.append(changes)
            
            # Calculate variance in interpretations
            var_dict = {}
            for var in interpretations[0].keys():
                values = [interp[var] for interp in interpretations]
                var_dict[var] = np.var(values)
            
            results.append({
                'prompt': prompt,
                'interpretation_variance': var_dict,
                'interpretations': interpretations
            })
        
        return results
    
    def plot_results(self, results):
        """Plot evaluation results"""
        # Create visualizations
        plt.figure(figsize=(15, 10))
        
        # Plot 1: MSE across folds
        plt.subplot(2, 2, 1)
        plt.plot(results['mse'])
        plt.title('MSE across folds')
        plt.xlabel('Fold')
        plt.ylabel('MSE')
        
        # Plot 2: R2 across folds
        plt.subplot(2, 2, 2)
        plt.plot(results['r2'])
        plt.title('R2 Score across folds')
        plt.xlabel('Fold')
        plt.ylabel('R2')
        
        plt.tight_layout()
        plt.savefig('../models/evaluation_results.png')
        plt.close()

if __name__ == "__main__":
    # Run evaluation
    simulator = EnvironmentSimulator()
    evaluator = ModelEvaluator(simulator)
    
    # Test prompts for semantic evaluation
    test_prompts = [
        "Reduce air pollution by 20% and increase green spaces by 15%",
        "Improve water quality by reducing industrial waste by 30%",
        "Decrease traffic congestion by 25% and increase public transportation by 20%"
    ]
    
    # Run all evaluations
    predictive_results = evaluator.evaluate_predictive_accuracy()
    causal_results = evaluator.evaluate_causal_consistency()
    uncertainty_results = evaluator.evaluate_uncertainty()
    semantic_results = evaluator.evaluate_semantic_reliability(test_prompts)
    
    # Save results
    evaluation_results = {
        'predictive': predictive_results,
        'causal': causal_results,
        'uncertainty': uncertainty_results,
        'semantic': semantic_results
    }
    
    with open('../models/evaluation_results.json', 'w') as f:
        json.dump(evaluation_results, f, indent=2)
    
    # Plot results
    evaluator.plot_results(predictive_results) 