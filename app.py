from flask import Flask, request, jsonify
from sqlalchemy import create_engine, text
import os
import logging
import datetime
import requests

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Database connection setup
TAX_DB_URI = os.getenv("TAX_DB_URI")
REBATE_DB_URI = os.getenv("REBATE_DB_URI")
USER_INPUT_SERVICE_BASE_URL = os.getenv("USER_INPUT_SERVICE_BASE_URL", "https://salary-calculator-user-input.onrender.com")

# Validate environment variables
if not TAX_DB_URI or not REBATE_DB_URI:
    raise ValueError("Environment variables TAX_DB_URI and REBATE_DB_URI must be set.")

logging.info(f"TAX_DB_URI: {TAX_DB_URI}")
logging.info(f"REBATE_DB_URI: {REBATE_DB_URI}")

# Create database engines
try:
    tax_engine = create_engine(TAX_DB_URI)
    rebate_engine = create_engine(REBATE_DB_URI)
except Exception as e:
    logging.error(f"Error creating database engines: {e}")
    raise

# Helper function to fetch user input from User Input Service
def fetch_user_input():
    """
    Fetch user input from the User Input Service.
    Returns:
        dict: Data returned from User Input Service.
    """
    url = f"{USER_INPUT_SERVICE_BASE_URL}/get-user-input"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Error fetching user input: {response.status_code} - {response.json().get('error', 'Unknown error')}")
            return {"error": response.json().get("error", "Unknown error")}
    except requests.RequestException as e:
        logging.error(f"Failed to connect to User Input Service: {e}")
        return {"error": "Connection to User Input Service failed"}

@app.route("/fetch-user-input", methods=["GET"])
def fetch_user_input_endpoint():
    """
    Endpoint to fetch user input from User Input Service.
    """
    logging.info("Accessing /fetch-user-input route")
    user_input = fetch_user_input()
    if "error" in user_input:
        return jsonify({"error": user_input["error"]}), 500
    return jsonify({"user_input": user_input}), 200

@app.route("/test-user-input-service", methods=["GET"])
def test_user_input_service():
    """
    Test connection with User Input Service.
    """
    url = f"{USER_INPUT_SERVICE_BASE_URL}/health"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            logging.info("User Input Service is healthy")
            return jsonify({"user_input_service_status": "Healthy"}), 200
        else:
            logging.warning("User Input Service is unhealthy")
            return jsonify({"user_input_service_status": "Unhealthy"}), 500
    except requests.RequestException as e:
        logging.error(f"Failed to connect to User Input Service: {e}")
        return jsonify({"error": f"Failed to connect: {e}"}), 500

@app.route("/get-tax-rate", methods=["POST"])
def get_tax_rate():
    """
    Fetch tax rate based on income.
    """
    logging.info("Accessing /get-tax-rate route")
    data = request.json

    # Validate input
    income = data.get("income")
    if not income:
        logging.error("Income is required")
        return jsonify({"error": "Income is required"}), 400
    if not isinstance(income, (int, float)) or income < 0:
        logging.error("Invalid income value")
        return jsonify({"error": "Invalid income value"}), 400

    # Execute query safely
    query = text("""
        SELECT rate
        FROM tax_table
        WHERE min_income <= :income AND max_income >= :income
    """)
    try:
        result = tax_engine.execute(query, {"income": income}).fetchone()
        if result:
            logging.info(f"Tax rate found: {result['rate']}")
            return jsonify({"tax_rate": result["rate"]}), 200
        else:
            logging.warning("Tax rate not found")
            return jsonify({"error": "Tax rate not found"}), 404
    except Exception as e:
        logging.error(f"Error executing query: {e}")
        return jsonify({"error": "Database error"}), 500

@app.route("/get-tax-details", methods=["POST"])
def get_tax_details():
    """
    Fetch applicable tax details.
    """
    logging.info("Accessing /get-tax-details route")
    data = request.json

    # Fetch missing user input from User Input Service if not provided
    if not all([data.get("month"), data.get("year"), data.get("income")]):
        user_input = fetch_user_input()
        if "error" in user_input:
            return jsonify({"error": user_input["error"]}), 500
        # Merge data with user input
        data = {**user_input, **data}

    # Validate input
    try:
        month = data["month"]
        year = data["year"]
        income = data["income"]

        # Convert month/year to datetime
        input_date = datetime.datetime(year, month, 1)

        # Query tax_table for the applicable tax table
        query = text("SELECT * FROM tax_table WHERE effective_date <= :date AND end_date >= :date")
        tax_table = tax_engine.execute(query, {"date": input_date}).fetchone()

        if tax_table:
            # Query specific tax period table based on income
            tax_table_name = tax_table["table_name"]
            query = text(f"SELECT * FROM {tax_table_name} WHERE min_income <= :income AND max_income >= :income")
            row = tax_engine.execute(query, {"income": income}).fetchone()

            if row:
                return jsonify({
                    "financial_year": tax_table["financial_year"],
                    "tax_percentage": row["tax_percentage"],
                    "tax_on_previous_bracket": row["tax_on_previous_bracket"]
                }), 200
            else:
                logging.warning("No matching tax row found")
                return jsonify({"error": "No matching tax row found"}), 404
        else:
            logging.warning("No applicable tax table found")
            return jsonify({"error": "No applicable tax table found"}), 404

    except Exception as e:
        logging.error(f"Error in /get-tax-details: {e}")
        return jsonify({"error": "Database error"}), 500

@app.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint.
    """
    return jsonify({"status": "OK"}), 200

if __name__ == "__main__":
    logging.info("Starting Flask app")
    app.run(host="0.0.0.0", port=5001)