from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Allows your frontend to talk to this API

# 1. The Database Backend API
@app.route('/api/verify/<khasra_no>', methods=['GET'])
def get_property(khasra_no):
    # This acts as your PostgreSQL database for the prototype
    mock_db = {
        "45/2": {
            "ownerName": "Rajesh Kumar",
            "area": 1.5,
            "encumbranceStatus": "Active Mortgage (SBI)"
        }
    }
    
    # Check if the khasra exists in our mock DB
    if khasra_no in mock_db:
        return jsonify(mock_db[khasra_no])
    else:
        return jsonify({"error": "Property not found"}), 404

# 2. The OCR Microservice API
@app.route('/api/scan', methods=['POST'])
def scan_document():
    # We are skipping actual Tesseract installation to ensure it runs instantly for you today.
    # We will simulate the OCR extraction delay and return mock data.
    import time
    time.sleep(1) 
    
    return jsonify({
        "status": "success",
        "mock_extracted_name": "Ramesh Kumar",
        "mismatch_found": True
    })

if __name__ == '__main__':
    app.run(port=5000, debug=True)