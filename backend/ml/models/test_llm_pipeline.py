import json
import numpy as np
from inference import EnvironmentSimulator
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional
import pandas as pd

class LLMPipelineTester:
    def __init__(self):
        """Initialize the pipeline tester with simulator"""
        self.simulator = EnvironmentSimulator()
        
    def test_llm_interpretation(self, test_cases: List[Dict[str, str]]) -> Dict[str, List[Dict]]:
        """
        Test LLM's ability to interpret user inputs and handle edge cases
        
        Args:
            test_cases: List of test cases with 'input' and 'expected_type' keys
        """
        results = {
            'successful_interpretations': [],
            'failed_interpretations': [],
            'reprompt_needed': []
        }
        
        for case in test_cases:
            print(f"\nTesting input: {case['input']}")
            try:
                # Get LLM interpretation
                changes = self.simulator.process_llm_input(case['input'])
                
                if not changes:
                    print("No changes detected - reprompt needed")
                    results['reprompt_needed'].append({
                        'input': case['input'],
                        'reason': 'No environmental changes detected'
                    })
                    continue
                
                # Validate changes against expected type
                if self._validate_changes(changes, case.get('expected_type', 'any')):
                    print("Successfully interpreted input")
                    results['successful_interpretations'].append({
                        'input': case['input'],
                        'changes': changes
                    })
                else:
                    print("Changes don't match expected type")
                    results['failed_interpretations'].append({
                        'input': case['input'],
                        'changes': changes,
                        'reason': 'Changes do not match expected type'
                    })
                    
            except Exception as e:
                print(f"Error processing input: {str(e)}")
                results['failed_interpretations'].append({
                    'input': case['input'],
                    'error': str(e)
                })
                
        return results
    
    def _validate_changes(self, changes: Dict[str, float], expected_type: str) -> bool:
        """Validate if changes match expected type with enhanced biodiversity recognition"""
        if expected_type == 'any':
            return True
            
        if expected_type == 'pollution':
            pollution_terms = ['Pollution', 'Contamination', 'Emissions', 'PM2.5', 'Ozone']
            return any(term in key for key in changes.keys() for term in pollution_terms)
            
        if expected_type == 'traffic':
            traffic_terms = ['Traffic', 'Transportation', 'Vehicles', 'Congestion']
            return any(term in key for key in changes.keys() for term in traffic_terms)
            
        if expected_type == 'biodiversity':
            biodiversity_terms = [
                'Biodiversity', 'Species', 'Habitat', 'Wildlife',
                'Ecosystem', 'Flora', 'Fauna', 'Conservation',
                'TerrHabRank', 'SpBioRnkEco', 'ClimVulVertCount'
            ]
            return any(term in key for key in changes.keys() for term in biodiversity_terms)
            
        return False
    
    def test_simulation_pipeline(self, changes: Dict[str, float]) -> Optional[Dict]:
        """Test full simulation pipeline with given changes and enhanced visualization"""
        try:
            # Run simulation
            impacts = self.simulator.simulate_changes(changes)
            
            if not impacts:
                print("No impacts generated from simulation")
                return None
            
            # Calculate confidence scores based on impact magnitudes
            confidence_scores = {
                var: min(abs(value) / 100, 1.0) 
                for var, value in impacts.items()
            }
            
            return {
                'changes': changes,
                'impacts': impacts,
                'confidence_scores': confidence_scores
            }
            
        except Exception as e:
            print(f"Error in simulation: {str(e)}")
            return None
    
    def visualize_results(self, results: Dict) -> None:
        """Create enhanced visualizations for simulation results"""
        if not results or 'impacts' not in results:
            print("No results to visualize")
            return
            
        try:
            # Create figure with subplots
            plt.figure(figsize=(15, 20))
            
            # Plot 1: Environmental Changes
            plt.subplot(4, 1, 1)
            changes = list(results['changes'].values())
            change_labels = [key.split('__')[-1][:20] for key in results['changes'].keys()]
            plt.bar(range(len(changes)), changes, alpha=0.7)
            plt.xticks(range(len(changes)), change_labels, rotation=45, ha='right')
            plt.title('Environmental Changes')
            plt.ylabel('Percentage Change')
            
            # Plot 2: Environmental Impacts
            plt.subplot(4, 1, 2)
            impacts = list(results['impacts'].values())
            impact_labels = [key.split('__')[-1][:20] for key in results['impacts'].keys()]
            bars = plt.bar(range(len(impacts)), impacts, alpha=0.7, color='orange')
            plt.xticks(range(len(impacts)), impact_labels, rotation=45, ha='right')
            plt.title('Environmental Impacts')
            plt.ylabel('Impact Score')
            
            # Add value labels on the bars
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1f}',
                        ha='center', va='bottom')
            
            # Plot 3: Confidence Scores
            plt.subplot(4, 1, 3)
            confidence_scores = list(results.get('confidence_scores', {}).values())
            if confidence_scores:
                plt.bar(range(len(confidence_scores)), confidence_scores, alpha=0.7, color='green')
                plt.xticks(range(len(confidence_scores)), impact_labels, rotation=45, ha='right')
                plt.title('Prediction Confidence Scores')
                plt.ylabel('Confidence (0-1)')
            
            # Plot 4: Combined Distribution
            plt.subplot(4, 1, 4)
            
            # Create separate DataFrames for changes and impacts
            changes_df = pd.DataFrame({
                'Type': change_labels,
                'Value': changes,
                'Category': ['Change'] * len(changes)
            })
            
            impacts_df = pd.DataFrame({
                'Type': impact_labels,
                'Value': impacts,
                'Category': ['Impact'] * len(impacts)
            })
            
            # Concatenate the DataFrames
            combined_df = pd.concat([changes_df, impacts_df])
            
            # Create boxplot with enhanced styling
            sns.boxplot(data=combined_df, x='Type', y='Value', hue='Category', palette='Set2')
            plt.xticks(rotation=45, ha='right')
            plt.title('Distribution of Changes and Impacts')
            plt.ylabel('Value')
            
            plt.tight_layout()
            
            # Save high-resolution visualization
            plt.savefig('llm_pipeline_results.png', bbox_inches='tight', dpi=300)
            plt.savefig('llm_pipeline_results.pdf', bbox_inches='tight')  # Vector format for better quality
            plt.close()
            
            print("Visualizations saved as 'llm_pipeline_results.png' and 'llm_pipeline_results.pdf'")
            
            # Print numerical summary with confidence scores
            print("\nNumerical Summary:")
            print("\nChanges:")
            for label, value in zip(change_labels, changes):
                print(f"{label}: {value:.2f}")
            
            print("\nImpacts:")
            for label, value, conf in zip(impact_labels, impacts, confidence_scores):
                print(f"{label}: {value:.2f} (confidence: {conf:.2f})")
            
        except Exception as e:
            print(f"Error creating visualization: {str(e)}")

def main():
    # Initialize tester
    tester = LLMPipelineTester()
    
    # Define test cases with enhanced biodiversity scenarios
    test_cases = [
        # Original test cases
        {
            'input': 'Reduce air pollution by 20% and increase green spaces by 15%',
            'expected_type': 'pollution'
        },
        {
            'input': 'Make the city more environmentally friendly',  # Vague input
            'expected_type': 'any'
        },
        {
            'input': 'Decrease traffic congestion by 30%',
            'expected_type': 'traffic'
        },
        
        # Enhanced biodiversity test cases
        {
            'input': 'Improve species diversity by 25% through habitat restoration',
            'expected_type': 'biodiversity'
        },
        {
            'input': 'Increase protected wildlife areas by 15% and reduce habitat fragmentation',
            'expected_type': 'biodiversity'
        },
        {
            'input': 'Enhance ecosystem resilience through conservation measures',
            'expected_type': 'biodiversity'
        },
        {
            'input': 'Protect endangered species by improving their natural habitats',
            'expected_type': 'biodiversity'
        },
        {
            'input': 'Implement wildlife corridors to connect fragmented habitats',
            'expected_type': 'biodiversity'
        },
        
        # Complex multi-factor cases
        {
            'input': 'Reduce pollution by 20% while increasing biodiversity through habitat protection',
            'expected_type': 'pollution'  # Primary focus
        },
        {
            'input': 'Create green corridors along highways to improve air quality and wildlife movement',
            'expected_type': 'biodiversity'  # Primary focus
        },
        
        # Edge cases
        {
            'input': 'xyz123',  # Invalid input
            'expected_type': 'any'
        },
        {
            'input': '',  # Empty input
            'expected_type': 'any'
        }
    ]
    
    # Test LLM interpretation
    print("Testing LLM interpretation...")
    interpretation_results = tester.test_llm_interpretation(test_cases)
    
    # Print interpretation results
    print("\nInterpretation Results:")
    print(f"Successful: {len(interpretation_results['successful_interpretations'])}")
    print(f"Failed: {len(interpretation_results['failed_interpretations'])}")
    print(f"Reprompt needed: {len(interpretation_results['reprompt_needed'])}")
    
    # Test simulation pipeline for successful interpretations
    print("\nTesting simulation pipeline...")
    for case in interpretation_results['successful_interpretations']:
        print(f"\nSimulating changes for: {case['input']}")
        simulation_results = tester.test_simulation_pipeline(case['changes'])
        
        if simulation_results:
            print("Creating visualizations...")
            tester.visualize_results(simulation_results)
        else:
            print("Simulation failed")
    
    # Save detailed results
    with open('llm_pipeline_test_results.json', 'w') as f:
        json.dump(interpretation_results, f, indent=2)

if __name__ == "__main__":
    main() 