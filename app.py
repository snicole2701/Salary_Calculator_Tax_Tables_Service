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

@app.route("/get-tax-details", methods=["POST"])
def get_tax_details():
    """
    Fetch applicable tax details and rebate details.
    """
    logging.info("Accessing /get-tax-details route")
    data = request.json

    # Fetch missing user input from User Input Service if not provided
    if not all([data.get("month"), data.get("year"), data.get("projected_annual_income"), data.get("projected_annual_income_plus_bonus_leave"), data.get("age_group")]):
        user_input = fetch_user_input()
        if "error" in user_input:
            return jsonify({"error": user_input["error"]}), 500
        # Merge data with user input
        data = {**user_input, **data}

    # Validate input
    try:
        month = data["month"]
        year = data["year"]
        age_group = data["age_group"]
        projected_annual_income = data["projected_annual_income"]
        projected_annual_income_plus_bonus_leave = data["projected_annual_income_plus_bonus_leave"]

        # Convert month/year to datetime
        input_date = datetime.datetime(year, month, 1)

        # Query tax_table for the applicable tax table
        query_tax_table = text("SELECT * FROM tax_table WHERE effective_date <= :date AND end_date >= :date")
        tax_table = tax_engine.execute(query_tax_table, {"date": input_date}).fetchone()

        if tax_table:
            tax_table_name = tax_table["table_name"]
            financial_year = tax_table["financial_year"]

            # Query tax details for projected_annual_income
            query_projected_income = text(f"""
                SELECT tax_percentage, tax_on_previous_bracket
                FROM {tax_table_name}
                WHERE min_income <= :income AND max_income >= :income
            """)
            row_projected_income = tax_engine.execute(query_projected_income, {"income": projected_annual_income}).fetchone()

            # Query tax details for projected_annual_income_plus_bonus_leave
            query_projected_income_plus_bonus_leave = text(f"""
                SELECT tax_percentage, tax_on_previous_bracket
                FROM {tax_table_name}
                WHERE min_income <= :income AND max_income >= :income
            """)
            row_projected_income_plus_bonus_leave = tax_engine.execute(query_projected_income_plus_bonus_leave, {"income": projected_annual_income_plus_bonus_leave}).fetchone()

            # Query rebate table for rebate details based on age_group and financial_year
            query_rebate_table = text("SELECT rebate_value FROM rebate_table WHERE age_group = :age_group AND financial_year = :financial_year")
            rebate_row = rebate_engine.execute(query_rebate_table, {"age_group": age_group, "financial_year": financial_year}).fetchone()

            if row_projected_income and row_projected_income_plus_bonus_leave and rebate_row:
                return jsonify({
                    "financial_year": financial_year,
                    "projected_annual_income_tax_percentage": row_projected_income["tax_percentage"],
                    "projected_annual_income_tax_on_previous_brackets": row_projected_income["tax_on_previous_bracket"],
                    "income_tax_percentage": row_projected_income_plus_bonus_leave["tax_percentage"],
                    "income_tax_on_previous_brackets": row_projected_income_plus_bonus_leave["tax_on_previous_bracket"],
                    "rebate_value": rebate_row["rebate_value"]
                }), 200
            else:
                logging.warning("No matching tax rows or rebate details found")
                return jsonify({"error": "No matching tax rows or rebate details found"}), 404
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