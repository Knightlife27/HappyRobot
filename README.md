# HappyRobot Carrier Sales Use Case

This project implements a carrier sales use case using the HappyRobot platform and a custom REST API. The AI assistant helps carriers find suitable loads for their trucks by validating their MC number and retrieving load details using a reference number.

## Project Structure
- `/api`: Contains the Flask application for the REST API.
- `/data`: Contains the `loads.csv` file, which serves as the data source for the API.
- `/docs`: Contains project documentation (this file).
- `/scripts`: (Optional) Contains helper scripts for setup or testing.

## REST API Documentation

### Endpoint
- **GET `/loads/{reference_number}`**: Retrieves load details by reference number.
  - **Input**: `reference_number` (path parameter).
  - **Output**: JSON object with load details (e.g., origin, destination, rate, etc.).
  - **Example Request**:
    ```bash
    GET /loads/12345
    ```
  - **Example Response**:
    ```json
    {
      "reference_number": "12345",
      "origin": "New York",
      "destination": "Los Angeles",
      "equipment_type": "Dry Van",
      "rate": "1500",
      "commodity": "Electronics"
    }
    ```

### Error Handling
- **404 Not Found**: Returned if the `reference_number` does not exist in the dataset.

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd <repository-folder>