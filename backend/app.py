from flask import Flask, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Flask app initialization
app = Flask(__name__)

# MongoDB connection using Atlas URI
MONGO_URI = os.getenv("MONGO_URI")
try:
    client = MongoClient(MONGO_URI)
    db = client["hacklytics"]            # Database name from your Atlas cluster
    collection = db["species"]           # Example collection (adjust as needed)
    print("✅ Successfully connected to MongoDB Atlas.")
except Exception as e:
    print(f"❌ Error connecting to MongoDB: {e}")

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

    # Example: Echo back received data
    return jsonify({
        "received_factors": payload,
        "message": "Factors updated successfully ✅"
    }), 200


# ======== MAIN ========
if __name__ == "__main__":
    # Run the Flask server
    app.run(debug=True, port=5000)