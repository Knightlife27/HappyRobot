from flask import Flask, jsonify, request, abort
import csv
import os
import re  # Import the regular expression module
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Path to the CSV file
CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), '../data/loads.csv')

# Global variable to store the loaded data
cached_loads = None

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
        return jsonify(load)
    else:
        abort(404, description="Load not found")

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
