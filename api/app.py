from flask import Flask, jsonify, request, abort
import csv
import os
import re
import logging
import requests

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Path to the CSV file
CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), '../data/loads.csv')

# Global variable to store the loaded data
cached_loads = None

# FMCSA API configuration
FMCSA_API_KEY = os.environ.get('FMCSA_API_KEY')
FMCSA_API_URL = 'https://mobile.fmcsa.dot.gov/qc/services/carriers/{}'

# Helper function to load CSV data into memory
def load_csv_data():
    global cached_loads
    if cached_loads:
        logging.info("Using cached CSV data")
        return cached_loads

    logging.info(f"Loading CSV from: {CSV_FILE_PATH}")
    loads = []
    try:
        with open(CSV_FILE_PATH, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                loads.append(row)
        cached_loads = loads
        logging.info(f"Successfully loaded {len(loads)} loads from CSV")
    except FileNotFoundError:
        logging.error("CSV file not found")
        abort(500, description="Internal Server Error: CSV file not found")
    except csv.Error as e:
        logging.error(f"Error parsing CSV: {e}")
        abort(500, description="Internal Server Error: Error parsing CSV")
    except Exception as e:
        logging.exception(f"Unexpected error loading CSV: {e}")
        abort(500, description="Internal Server Error: Unexpected error")
    return loads

def validate_carrier(mc_number):
    """
    Validates the MC number using the FMCSA API.
    """
    if not FMCSA_API_KEY:
        logging.error("FMCSA API key not found in environment variables")
        return False, "FMCSA API key not configured"

    try:
        response = requests.get(
            FMCSA_API_URL.format(mc_number),
            headers={'X-API-Key': FMCSA_API_KEY}
        )
        response.raise_for_status()
        data = response.json()

        allow_to_operate = data.get("allowToOperate") == "Y"
        out_of_service = data.get("outOfService") == "N"

        is_valid = allow_to_operate and not out_of_service

        if not is_valid:
            reason = "Carrier not allowed to operate" if not allow_to_operate else "Carrier is out of service"
            return False, reason

        return True, None

    except requests.RequestException as e:
        logging.error(f"Error validating carrier with FMCSA API: {e}")
        return False, "Error communicating with FMCSA API"

# Endpoint to retrieve load details by reference number
@app.route('/loads/<reference_number>', methods=['GET'])
def get_load_by_reference(reference_number):
    # Input validation: Check if the reference number is valid
    if not re.match(r'^[a-zA-Z0-9]+$', reference_number):
        abort(400, description="Invalid reference number. Must be alphanumeric.")

    logging.info(f"Fetching load for reference_number: {reference_number}")
    loads = load_csv_data()
    load = next((load for load in loads if load['reference_number'] == reference_number), None)
    
    if load:
        # Validate carrier before returning load details
        mc_number = request.args.get('mc_number')
        if mc_number:
            is_valid, error_message = validate_carrier(mc_number)
            if not is_valid:
                if error_message:
                    logging.warning(f"Carrier validation failed for MC {mc_number}: {error_message}")
                    abort(400, description=f"Carrier validation failed: {error_message}")
                else:
                    logging.warning(f"Carrier validation failed for MC {mc_number}: Unknown reason")
                    abort(400, description="Carrier validation failed: Unknown reason")
        return jsonify(load)
    else:
        abort(404, description="Load not found")

# New route for validating carrier
@app.route('/validate_carrier/<mc_number>', methods=['GET'])
def validate_carrier_route(mc_number):
    is_valid, error_message = validate_carrier(mc_number)
    if error_message:
        logging.warning(f"Carrier validation failed for MC {mc_number}: {error_message}")
        return jsonify({"valid": is_valid, "error": error_message}), 400
    return jsonify({"valid": is_valid})

# Error handler for 400 (Bad Request)
@app.errorhandler(400)
def bad_request(e):
    logging.warning(f"Bad Request: {e}")
    return jsonify(error=str(e)), 400

# Error handler for 404 (Not Found)
@app.errorhandler(404)
def resource_not_found(e):
    logging.warning(f"Resource not found: {e}")
    return jsonify(error=str(e)), 404

# Error handler for 500 (Internal Server Error)
@app.errorhandler(500)
def internal_server_error(e):
    logging.error(f"Internal Server Error: {e}")
    return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run(debug=True)
