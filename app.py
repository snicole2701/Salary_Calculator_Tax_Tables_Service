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
TAX_DB_URI = os.getenv("TAX_DB_URI", "sqlite:///tax_database.db")
REBATE_DB_URI = os.getenv("REBATE_DB_URI", "sqlite:///rebate_database.db")
USER_INPUT_SERVICE_BASE_URL = os.getenv("USER_INPUT_SERVICE_BASE_URL", "https://salary-calculator-user-input.onrender.com")
CALCULATION_SERVICE_BASE_URL = os.getenv("CALCULATION_SERVICE_BASE_URL", "https://salary-calculator-calculation-service.onrender.com")

# Validate environment variables
if not TAX_DB_URI or not REBATE_DB_URI:
    raise ValueError("Environment variables TAX_DB_URI and REBATE_DB_URI must be set.")

logging.info(f"TAX_DB_URI: {TAX_DB_URI}")
logging.info(f"REBATE_DB_URI: {REBATE_DB_URI}")
logging.info(f"USER_INPUT_SERVICE_BASE_URL: {USER_INPUT_SERVICE_BASE_URL}")
logging.info(f"CALCULATION_SERVICE_BASE_URL: {CALCULATION_SERVICE_BASE_URL}")

# Create database engines
try:
    tax_engine = create_engine(TAX_DB_URI, future=True)
    rebate_engine = create_engine(REBATE_DB_URI, future=True)
except Exception as e:
    logging.error(f"Error creating database engines: {e}")
    raise

# Root route
@app.route("/", methods=["GET"])
def home():
    """Welcome route for the service."""
    return "Welcome to the Tax Table Service!", 200

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

# Helper function to forward data to Calculation Service
def send_to_calculation_service(data):
    """
    Send tax details and rebate details to Calculation Service.
    Args:
        data (dict): Tax and rebate details to send.
    Returns:
        dict: Response from Calculation Service.
    """
    url = f"{CALCULATION_SERVICE_BASE_URL}/receive-tax-rebate-details"
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            logging.info("Tax and rebate details successfully sent to Calculation Service.")
            return response.json()
        else:
            logging.error(f"Error sending tax and rebate details: {response.status_code} - {response.json().get('error', 'Unknown error')}")
            return {"error": response.json().get("error", "Unknown error")}
    except requests.RequestException as e:
        logging.error(f"Failed to connect to Calculation Service: {e}")
        return {"error": "Connection to Calculation Service failed"}

@app.route("/get-tax-details", methods=["POST"])
def get_tax_details():
    """
    Fetch applicable tax details and rebate details.
    """
    logging.info("Accessing /get-tax-details route")
    data = request.json

    # Fetch missing user input from User Input Service if not provided
    if not all([data.get("month"), data.get("year"), data.get("age_group")]):
        user_input = fetch_user_input()
        if "error" in user_input:
            return jsonify({"error": user_input["error"]}), 500
        # Merge data with user input
        data = {**user_input, **data}

    # Validate and prepare data for calculation
    try:
        month = data["month"]
        year = data["year"]
        age_group = data["age_group"]
        projected_annual_income = data["projected_annual_income"]
        projected_annual_income_plus_bonus_leave = data["projected_annual_income_plus_bonus_leave"]

        input_date = datetime.datetime(year, month, 1)

        # Find the relevant tax period table
        relevant_table = None
        with tax_engine.connect() as connection:
            tables_query = text("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'tax_period_%';")
            tables = connection.execute(tables_query).fetchall()
            logging.info(f"Available tax period tables: {[table[0] for table in tables]}")

            for table in tables:
                table_name = table[0]
                check_date_query = text(f"SELECT COUNT(*) FROM {table_name} WHERE effective_date <= :date AND end_date >= :date;")
                count = connection.execute(check_date_query, {"date": input_date}).scalar()
                if count > 0:
                    relevant_table = table_name
                    break

            if not relevant_table:
                logging.warning("No applicable tax period table found")
                return jsonify({"error": "No applicable tax period table found"}), 404

            logging.info(f"Relevant tax period table: {relevant_table}")

            # Query the relevant table for the projected income details
            income_query = text(f"""
                SELECT min_income, tax_on_previous_bracket, tax_percentage
                FROM {relevant_table}
                WHERE min_income <= :income AND max_income >= :income;
            """)
            row_projected_income = connection.execute(income_query, {"income": projected_annual_income}).fetchone()

            if not row_projected_income:
                logging.warning("No matching tax row found for projected_annual_income")
                return jsonify({"error": "No matching tax row for projected_annual_income"}), 404

        # Query the rebate table for rebate details
        with rebate_engine.connect() as connection:
            rebate_query = text("SELECT rebate_value FROM rebate_table WHERE age_group = :age_group AND financial_year = :financial_year")
            rebate_row = connection.execute(rebate_query, {"age_group": age_group, "financial_year": year}).fetchone()

            if not rebate_row:
                logging.warning("No matching rebate row found")
                return jsonify({"error": "No matching rebate row found"}), 404

        # Compile tax details
        tax_details = {
            "financial_year": year,
            "projected_annual_income_min_income": row_projected_income["min_income"],
            "projected_annual_income_tax_on_previous_brackets": row_projected_income["tax_on_previous_bracket"],
            "projected_annual_income_tax_percentage": row_projected_income["tax_percentage"],
            "rebate_value": rebate_row["rebate_value"]
        }

        # Send tax and rebate details to Calculation Service
        response_to_calculation_service = send_to_calculation_service(tax_details)
        if "error" in response_to_calculation_service:
            return jsonify({"error": response_to_calculation_service["error"]}), 500

        return jsonify(response_to_calculation_service), 200

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