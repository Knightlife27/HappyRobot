from flask import Flask, jsonify, request, abort
import csv
import os

app = Flask(__name__)

# Path to the CSV file (updated to reflect the correct folder structure)
CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), '../data/loads.csv')
print(f"CSV_FILE_PATH: {CSV_FILE_PATH}")  # Debug: Print the CSV file path

# Global variable to store the loaded data
cached_loads = None

# Helper function to load CSV data into memory
def load_csv_data():
    global cached_loads  # Declare that we're using the global variable
    if cached_loads:
        print("Using cached CSV data")  # Debug: Indicate that we're using the cache
        return cached_loads

    print(f"Loading CSV from: {CSV_FILE_PATH}")  # Debug: Print the CSV file path
    loads = []
    try:
        with open(CSV_FILE_PATH, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                print(f"Row: {row}")  # Debug: Print each row
                loads.append(row)
        print(f"Loaded data: {loads}")  # Debug: Print the loaded data
        cached_loads = loads  # Cache the loaded data
    except FileNotFoundError:
        print("Error: CSV file not found")  # Debug: Print if file is missing
    except Exception as e:
        print(f"Error loading CSV: {e}")  # Debug: Print any other errors
    return loads

# Endpoint to retrieve load details by reference number
@app.route('/loads/<reference_number>', methods=['GET'])
def get_load_by_reference(reference_number):
    print(f"Fetching load for reference_number: {reference_number}")  # Debug: Print the reference number
    loads = load_csv_data()
    load = next((load for load in loads if load['reference_number'] == reference_number), None)
    
    if load:
        return jsonify(load)
    else:
        abort(404, description="Load not found")

# Error handler for 404
@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404

if __name__ == '__main__':
    app.run(debug=True)
