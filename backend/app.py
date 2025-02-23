from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from collections import Counter
import vertexai
from vertexai.generative_models import GenerativeModel
from ml.models.inference import EnvironmentSimulator
import numpy as np
import json
import threading
import time

# Load environment variables from .env
load_dotenv()

# Flask app initialization with SocketIO
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize environment simulator
try:
    simulator = EnvironmentSimulator()
    print("✅ Successfully initialized Environment Simulator.")
except Exception as e:
    print(f"❌ Error initializing Environment Simulator: {e}")
    simulator = None

# Store active simulations
active_simulations = {}

def emit_simulation_updates(simulation_id, changes):
    """Background task to emit simulation updates"""
    try:
        # Initial state
        current_state = {var: 50 for var in simulator.key_variables['environmental_state']}
        
        # Emit initial state
        socketio.emit('simulation_update', {
            'simulation_id': simulation_id,
            'state': current_state,
            'step': 0
        })
        
        # Simulate gradual changes over 10 steps
        for step in range(1, 11):
            # Calculate intermediate state
            for var, target_change in changes.items():
                step_change = target_change / 10
                if var in current_state:
                    current_state[var] += step_change
            
            # Get impacts for current state
            impacts = simulator.simulate_changes(current_state)
            
            # Emit update
            socketio.emit('simulation_update', {
                'simulation_id': simulation_id,
                'state': current_state,
                'impacts': impacts,
                'step': step
            })
            
            time.sleep(1)  # 1-second delay between updates
            
        # Mark simulation as complete
        active_simulations[simulation_id]['status'] = 'complete'
        socketio.emit('simulation_complete', {
            'simulation_id': simulation_id,
            'final_state': current_state,
            'final_impacts': impacts
        })
        
    except Exception as e:
        print(f"Error in simulation updates: {str(e)}")
        socketio.emit('simulation_error', {
            'simulation_id': simulation_id,
            'error': str(e)
        })

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")

@socketio.on('start_simulation')
def handle_simulation_start(data):
    """Handle start of a new simulation"""
    try:
        message = data.get('message', '')
        simulation_id = data.get('simulation_id', request.sid)
        
        # Get LLM interpretation
        initial_response = get_ai_response(message)
        changes = parse_environmental_changes(initial_response)
        
        if not changes:
            emit('simulation_error', {
                'simulation_id': simulation_id,
                'error': 'No environmental changes detected in message'
            })
            return
        
        # Store simulation info
        active_simulations[simulation_id] = {
            'status': 'running',
            'changes': changes,
            'start_time': time.time()
        }
        
        # Start background thread for updates
        thread = threading.Thread(
            target=emit_simulation_updates,
            args=(simulation_id, changes)
        )
        thread.start()
        
        emit('simulation_started', {
            'simulation_id': simulation_id,
            'changes': changes
        })
        
    except Exception as e:
        emit('simulation_error', {
            'simulation_id': simulation_id,
            'error': str(e)
        })

@socketio.on('get_simulation_status')
def handle_status_request(data):
    """Handle requests for simulation status"""
    simulation_id = data.get('simulation_id', request.sid)
    if simulation_id in active_simulations:
        emit('simulation_status', {
            'simulation_id': simulation_id,
            'status': active_simulations[simulation_id]['status']
        })
    else:
        emit('simulation_status', {
            'simulation_id': simulation_id,
            'status': 'not_found'
        })

# MongoDB connection using Atlas URI
MONGO_URI = os.getenv("MONGO_URI")
try:
    client = MongoClient(MONGO_URI)
    db = client["hacklytics"]            # Database name from your Atlas cluster
    collection = db["species"]           # Example collection (adjust as needed)
    print("✅ Successfully connected to MongoDB Atlas.")
except Exception as e:
    print(f"❌ Error connecting to MongoDB: {e}")

messages = []

# Initialize Vertex AI
try:
    PROJECT_ID = "ecosim-451804"
    vertexai.init(project=PROJECT_ID, location="us-central1")
    model = GenerativeModel("gemini-1.5-flash-002")
    print("✅ Successfully initialized Vertex AI.")
except Exception as e:
    print(f"❌ Error initializing Vertex AI: {e}")

def get_ai_response(user_message, simulation_results=None):
    """
    Takes the user message and optional simulation results to generate a response.
    """
    try:
        # Create a context-aware prompt
        if simulation_results:
            prompt = f"""You are an environmental impact analysis AI. The user has proposed the following change: "{user_message}"

Based on our simulation, here are the impacts:
{json.dumps(simulation_results, indent=2)}

Analyze these results and explain their significance in a clear, engaging way. Focus on:
1. The most significant changes
2. Any potential risks or benefits
3. Suggestions for optimization if applicable

Keep your response concise but informative."""
        else:
            prompt = f"""You are an environmental impact analysis AI. The user has said: "{user_message}"

Extract any environmental changes they're proposing. Look for:
1. Specific numerical changes (e.g., "increase solar by 20%")
2. General directional changes (e.g., "reduce pollution")
3. Target areas (e.g., "focus on renewable energy")

If no specific changes are mentioned, ask for clarification about what environmental factors they'd like to modify."""

        print(f"Sending prompt to Vertex AI: {prompt}")  # Debug log
        response = model.generate_content(prompt)
        print(f"Received response from Vertex AI: {response.text}")  # Debug log
        return response.text
    except Exception as e:
        print(f"Error generating AI response: {str(e)}")
        return "I apologize, but I'm having trouble processing your message right now."

def parse_environmental_changes(llm_response):
    """
    Parse the LLM response to extract environmental changes with specific numerical values.
    """
    try:
        # Comprehensive mapping of terms to our model variables
        variable_mappings = {
            # Environmental Pressure variables
            ('pollution', 'pollutant', 'contamination'): 'calenviroscreen_3.0_results_june_2018_update__Pollution Burden Score',
            ('traffic', 'vehicles', 'transportation'): 'calenviroscreen_3.0_results_june_2018_update__Traffic',
            ('pesticide', 'herbicide', 'agricultural chemicals'): 'calenviroscreen_3.0_results_june_2018_update__Pesticides',
            ('diesel', 'fuel emissions', 'exhaust'): 'calenviroscreen_3.0_results_june_2018_update__Diesel PM',
            ('toxic', 'hazardous waste', 'chemical release'): 'calenviroscreen_3.0_results_june_2018_update__Tox. Release',
            
            # Environmental State variables
            ('ozone', 'o3', 'smog'): 'calenviroscreen_3.0_results_june_2018_update__Ozone',
            ('pm2.5', 'particulate matter', 'air particles'): 'calenviroscreen_3.0_results_june_2018_update__PM2.5',
            ('biodiversity', 'species diversity', 'ecosystem diversity'): 'Species_Biodiversity___ACE_[ds2769]__SpBioRnkEco',
            ('habitat', 'natural area', 'wildlife area'): 'Species_Biodiversity___ACE_[ds2769]__TerrHabRank'
        }
        
        import re
        
        # Pattern to match percentage changes
        percentage_pattern = r'(increase|decrease|reduce|improve|lower|raise|change)\s+(?:in\s+)?(?:the\s+)?([a-zA-Z\s]+)\s+(?:by\s+)?(\d+)(?:\s*%|\s+percent)'
        
        # Pattern to match absolute value changes
        absolute_pattern = r'(increase|decrease|reduce|improve|lower|raise|change)\s+(?:in\s+)?(?:the\s+)?([a-zA-Z\s]+)\s+(?:from|to)\s+(\d+)(?:\s*%|\s+percent)'
        
        changes = {}
        
        # Find all matches in the text
        matches = re.finditer(percentage_pattern, llm_response.lower()) 
        matches = list(matches) + list(re.finditer(absolute_pattern, llm_response.lower()))
        
        for match in matches:
            action, term, value = match.groups()
            value = float(value)
            
            # Convert action to direction
            direction = 1 if action in ['increase', 'improve', 'raise'] else -1
            
            # Find matching variable
            for terms, variable in variable_mappings.items():
                if any(t in term for t in terms):
                    changes[variable] = direction * value
                    break
        
        # If no specific changes found but terms are mentioned, use default changes
        if not changes:
            for terms, variable in variable_mappings.items():
                if any(t in llm_response.lower() for t in terms):
                    # Default to 10% change, direction based on context
                    direction = 1 if any(pos in llm_response.lower() for pos in ['increase', 'improve', 'better']) else -1
                    changes[variable] = direction * 10
        
        print(f"Parsed changes: {changes}")  # Debug log
        return changes
        
    except Exception as e:
        print(f"Error parsing environmental changes: {str(e)}")
        return {}

@app.route("/api/simulate", methods=["POST"])
def simulate_changes():
    """
    Endpoint to simulate environmental changes based on user input.
    """
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({"error": "No message provided"}), 400

        message = data['message']
        
        # First, get LLM interpretation of the message
        initial_response = get_ai_response(message)
        
        # Parse the response to get environmental changes
        changes = parse_environmental_changes(initial_response)
        
        if not changes:
            return jsonify({
                "status": "clarification_needed",
                "message": initial_response
            }), 200
        
        # Run simulation if we have valid changes
        if simulator:
            impacts = simulator.simulate_changes(changes)
            
            # Get AI analysis of the results
            analysis = get_ai_response(message, impacts)
            
            return jsonify({
                "status": "success",
                "changes": changes,
                "impacts": impacts,
                "analysis": analysis
            }), 200
        else:
            return jsonify({"error": "Simulator not initialized"}), 500
            
    except Exception as e:
        return jsonify({"error": f"Failed to simulate changes: {str(e)}"}), 500

# ======== ROUTES ========

@app.route("/api/hello", methods=["GET"])
def hello_world():
    """ Basic endpoint to confirm Flask server is running. """
    return jsonify({"message": "Hello from Flask! Connection is working ✅"})


@app.route("/api/data", methods=["GET"])
def get_data():
    """
    Returns all documents from the 'species' collection.
    Adjust the collection or fields as necessary.
    """
    try:
        data = list(collection.find({}, {"_id": 0}))  # Exclude _id for cleaner output
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch data: {str(e)}"}), 500


@app.route("/api/update_factor", methods=["POST"])
def update_factor():
    """
    Receives factor updates from the user (e.g., deforestation, poaching).
    In the real app, this is where the model inference or database updates would happen.
    """
    payload = request.json
    if not payload:
        return jsonify({"error": "No data received in request."}), 400

    return jsonify({
        "received_factors": payload,
        "message": "Factors updated successfully ✅"
    }), 200


@app.route("/api/messages", methods=["POST"])
def store_message():
    """
    Stores a message and returns the last message sent along with AI response.
    """
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({"error": "No message provided"}), 400

        message = data['message']
        messages.append(message)
        
        # Get AI response
        ai_response = get_ai_response(message)
        messages.append(ai_response)  # Store AI response too
        
        return jsonify({
            "status": "success",
            "lastMessage": {
                "text": message,
                "index": len(messages) - 2
            },
            "aiResponse": {
                "text": ai_response,
                "isSystem": True
            }
        }), 200

    except Exception as e:
        return jsonify({"error": f"Failed to process message: {str(e)}"}), 500

@app.route("/api/messages/last", methods=["GET"])
def get_last_message():
    """
    Returns the last message sent.
    """
    try:
        if not messages:
            return jsonify({"message": "No messages stored yet"}), 200
            
        last_message = messages[-1]
        
        return jsonify({
            "text": last_message,
            "index": len(messages) - 1
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get last message: {str(e)}"}), 500

@app.route("/api/variables", methods=["GET"])
def get_variables():
    """
    Returns available environmental variables that can be modified.
    """
    try:
        if not simulator:
            return jsonify({"error": "Simulator not initialized"}), 500
            
        # Get variables from simulator
        variables = {
            'pressure': simulator.key_variables.get('environmental_pressure', []),
            'state': simulator.key_variables.get('environmental_state', []),
            'impact': simulator.key_variables.get('impact', [])
        }
        
        # Add friendly names and descriptions
        formatted_variables = {}
        for category, vars in variables.items():
            formatted_variables[category] = [{
                'id': var,
                'name': var.split('__')[-1].replace('_', ' ').title(),
                'description': f"Measures the {var.split('__')[-1].lower()}",
                'category': category
            } for var in vars]
        
        return jsonify(formatted_variables), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to get variables: {str(e)}"}), 500

# ======== MAIN ========
if __name__ == "__main__":
    # Run the Flask server with SocketIO
    socketio.run(app, debug=True, port=5000)