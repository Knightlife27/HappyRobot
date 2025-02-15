# app.py
from flask import Flask, jsonify, request, abort
import csv
import os

app = Flask(__name__)

# Path to the CSV file (we'll place it in the /data folder later)
CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), '../data/loads.csv')

# Helper function to load CSV data into memory
def load_csv_data():
    loads = []
    with open(CSV_FILE_PATH, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            loads.append(row)
    return loads

# Endpoint to retrieve load details by reference number
@app.route('/loads/<reference_number>', methods=['GET'])
def get_load_by_reference(reference_number):
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