from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List
from ml.models.inference import EnvironmentSimulator

router = APIRouter()
simulator = EnvironmentSimulator()

class SimulationRequest(BaseModel):
    user_input: str
    selected_features: List[str]

@router.post("/simulate")
async def simulate_environment(request: SimulationRequest):
    try:
        # Process LLM input
        changes = simulator.process_llm_input(request.user_input)
        
        # Filter changes based on selected features
        filtered_changes = {k: v for k, v in changes.items() 
                          if any(feature in k for feature in request.selected_features)}
        
        # Get impacts
        impacts = simulator.simulate_changes(filtered_changes)
        
        return {
            "changes": changes,
            "impacts": impacts,
            "feature_importance": simulator.get_feature_importance()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 