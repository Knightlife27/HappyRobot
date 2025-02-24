# from flask import Flask, jsonify, request, abort
# import csv
# import os
# import re
# import logging
# import requests
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

# # Configure logging
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# # Print API key for debugging (remove in production)
# logging.info(f"Loaded API Key: {os.environ.get('FMCSA_API_KEY')[:5]}...") # Only show first 5 characters

# app = Flask(__name__)

# # Path to the CSV file
# CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), '../data/loads.csv')

# # Global variable to store the loaded data
# cached_loads = None

# # FMCSA API configuration
# FMCSA_API_KEY = os.environ.get('FMCSA_API_KEY', '').strip()
# FMCSA_API_BASE_URL = 'https://mobile.fmcsa.dot.gov/qc/services/'

# # Helper function to load CSV data into memory
# def load_csv_data():
#     global cached_loads
#     if cached_loads:
#         logging.info("Using cached CSV data")
#         return cached_loads

#     logging.info(f"Loading CSV from: {CSV_FILE_PATH}")
#     loads = []
#     try:
#         with open(CSV_FILE_PATH, mode='r') as file:
#             reader = csv.DictReader(file)
#             for row in reader:
#                 loads.append(row)
#         cached_loads = loads
#         logging.info(f"Successfully loaded {len(loads)} loads from CSV")
#     except FileNotFoundError:
#         logging.error("CSV file not found")
#         abort(500, description="Internal Server Error: CSV file not found")
#     except csv.Error as e:
#         logging.error(f"Error parsing CSV: {e}")
#         abort(500, description="Internal Server Error: Error parsing CSV")
#     except Exception as e:
#         logging.exception(f"Unexpected error loading CSV: {e}")
#         abort(500, description="Internal Server Error: Unexpected error")
#     return cached_loads

# def validate_mc_number(mc_number):
#     try:
#         # Convert scientific notation to integer
#         mc_number = int(float(mc_number))
#         mc_number_str = str(mc_number)
#         if not re.fullmatch(r'\d{7}', mc_number_str):
#             return False, "MC number must be exactly 7 digits"
#         return True, mc_number_str
#     except ValueError:
#         return False, "Invalid MC number format"

# def validate_carrier(mc_number):
#     """
#     Validates the MC number using the FMCSA API.
#     """
#     logging.info(f"Starting carrier validation for MC number: {mc_number}")
#     if not FMCSA_API_KEY:
#         logging.error("FMCSA API key not found in environment variables")
#         return False, "FMCSA API key not configured"

#     try:
#         url = f"{FMCSA_API_BASE_URL}carriers/{mc_number}"
#         params = {
#             'webKey': FMCSA_API_KEY
#         }
#         logging.info(f"Sending request to FMCSA API: {url}")
#         logging.info(f"API Key being used: {FMCSA_API_KEY[:5]}...")  # Log first 5 characters of API key
        
#         response = requests.get(url, params=params)
#         logging.info(f"Full URL being called: {response.url}")
#         logging.info(f"FMCSA API response status code: {response.status_code}")
#         logging.info(f"FMCSA API response headers: {response.headers}")
#         logging.debug(f"FMCSA API full response content: {response.text}")

#         if response.status_code == 500:
#             logging.error("FMCSA API returned a 500 error. This might be a temporary issue.")
#             return False, "FMCSA API is currently unavailable. Please try again later."

#         response.raise_for_status()
#         data = response.json()
#         logging.debug(f"Parsed JSON data: {data}")

#         # Check if the carrier data is present in the response
#         if not data or 'content' not in data or not data['content']:
#             logging.warning("No carrier data found in the API response")
#             return False, "No carrier data found"
        
#         carrier_data = data['content']['carrier']
#         logging.info(f"Carrier data retrieved: {carrier_data}")

#         allow_to_operate = carrier_data.get("allowedToOperate") == "Y"
#         out_of_service = carrier_data.get("oosDate") is not None

#         is_valid = allow_to_operate and not out_of_service

#         if not is_valid:
#             reason = "Carrier not allowed to operate" if not allow_to_operate else "Carrier is out of service"
#             logging.warning(f"Carrier validation failed: {reason}")
#             return False, reason

#         logging.info("Carrier validation successful")
#         return True, None

#     except requests.RequestException as e:
#         logging.error(f"Error validating carrier with FMCSA API: {e}")
#         if e.response is not None:
#             logging.error(f"Response status code: {e.response.status_code}")
#             logging.error(f"Response content: {e.response.text}")
#         return False, f"Error communicating with FMCSA API: {str(e)}"

# # New route for root URL
# @app.route('/', methods=['GET'])
# def home():
#     logging.info("Home route accessed")
#     return jsonify({"message": "Welcome to the HappyRobot API"}), 200

# # Endpoint to retrieve load details by reference number
# @app.route('/loads/<reference_number>', methods=['GET'])
# def get_load_by_reference(reference_number):
#     logging.info(f"Load details requested for reference number: {reference_number}")
    
#     # Input validation: Check if the reference number is valid
#     if not re.fullmatch(r'\d{7}', reference_number):
#         logging.warning(f"Invalid reference number provided: {reference_number}")
#         abort(400, description="Invalid reference number. Must be exactly 7 digits.")
    
#     loads = load_csv_data()
#     load = next((load for load in loads if load['reference_number'] == reference_number), None)
    
#     if load:
#         logging.info(f"Load found for reference number {reference_number}")
#         # Validate carrier before returning load details
#         mc_number = request.args.get('mc_number')
#         if mc_number:
#             logging.info(f"Validating carrier with MC number: {mc_number}")
#             is_valid, result = validate_mc_number(mc_number)
#             if not is_valid:
#                 logging.warning(f"MC number validation failed: {result}")
#                 abort(400, description=f"MC number validation failed: {result}")
#             is_valid, error_message = validate_carrier(result)
#             if not is_valid:
#                 logging.warning(f"Carrier validation failed for MC {result}: {error_message}")
#                 abort(400, description=f"Carrier validation failed: {error_message}")
#         return jsonify(load)
#     else:
#         logging.warning(f"Load not found for reference number: {reference_number}")
#         abort(404, description="Load not found")

# # New route for validating carrier
# @app.route('/validate_carrier', methods=['GET'])
# def validate_carrier_route():
#     mc_number = request.args.get('mc_number')
#     logging.info(f"Carrier validation requested for MC number: {mc_number}")

#     is_valid, result = validate_mc_number(mc_number)
#     if not is_valid:
#         logging.warning(f"MC number validation failed: {result}")
#         return jsonify({"valid": False, "error": result}), 400

#     is_valid, error_message = validate_carrier(result)
#     if error_message:
#         logging.warning(f"Carrier validation failed for MC {result}: {error_message}")
#         return jsonify({"valid": is_valid, "error": error_message}), 400
#     logging.info(f"Carrier validation successful for MC {result}")
#     return jsonify({"valid": is_valid})

# # Error handler for 400 (Bad Request)
# @app.errorhandler(400)
# def bad_request(e):
#     logging.warning(f"Bad Request: {e}")
#     return jsonify(error=str(e)), 400

# # Error handler for 404 (Not Found)
# @app.errorhandler(404)
# def resource_not_found(e):
#     logging.warning(f"Resource not found: {e}")
#     return jsonify(error=str(e)), 404

# # Error handler for 500 (Internal Server Error)
# @app.errorhandler(500)
# def internal_server_error(e):
#     logging.error(f"Internal Server Error: {e}")
#     return jsonify(error=str(e)), 500

# if __name__ == '__main__':
#     logging.info("Starting the Flask application")
#     app.run(debug=True)
