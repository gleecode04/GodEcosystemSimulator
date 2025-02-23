from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from collections import Counter
import vertexai
from vertexai.generative_models import GenerativeModel

# Load environment variables from .env
load_dotenv()

# Flask app initialization
app = Flask(__name__)
CORS(app)

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

def get_ai_response(user_message):
    """
    Takes the last user message and returns an AI-generated response.
    """
    try:
        prompt = f"""Respond to the user's message in a friendly and engaging manner. The user's message is: {user_message}"""
        print(f"Sending prompt to Vertex AI: {prompt}")  # Debug log
        response = model.generate_content(prompt)
        print(f"Received response from Vertex AI: {response.text}")  # Debug log
        return response.text
    except Exception as e:
        print(f"Error generating AI response: {str(e)}")
        print(f"Error type: {type(e)}")  # Print the type of error
        return "I apologize, but I'm having trouble processing your message right now."

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

# ======== MAIN ========
if __name__ == "__main__":
    # Run the Flask server
    app.run(debug=True, port=5000)