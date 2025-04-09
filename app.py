from flask import Flask, request, jsonify
from sqlalchemy import create_engine, text
import os
import logging
import datetime

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Database connection setup
TAX_DB_URI = os.getenv("TAX_DB_URI")
REBATE_DB_URI = os.getenv("REBATE_DB_URI")

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

# Routes
@app.route("/")
def home():
    logging.info("Accessing / route")
    return "Welcome to the Tax Table Service!"

@app.route("/get-tax-rate", methods=["POST"])
def get_tax_rate():
    """Fetch tax rate based on income."""
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
    """Fetch applicable tax details."""
    data = request.json

    # Validate input
    month = data.get("month")
    year = data.get("year")
    income = data.get("income")
    if not all([month, year, income]):
        return jsonify({"error": "Month, year, and income are required"}), 400

    try:
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
                return jsonify({"error": "No matching tax row found"}), 404
        else:
            return jsonify({"error": "No applicable tax table found"}), 404

    except Exception as e:
        logging.error(f"Error in /get-tax-details: {e}")
        return jsonify({"error": "Database error"}), 500

@app.route("/get-rebate", methods=["POST"])
def get_rebate():
    """Fetch rebate amount based on criteria."""
    logging.info("Accessing /get-rebate route")
    data = request.json

    # Validate input
    criteria = data.get("criteria")
    if not criteria:
        logging.error("Criteria is required")
        return jsonify({"error": "Criteria is required"}), 400

    # Execute query safely
    query = text("SELECT amount FROM rebate_table WHERE criteria = :criteria")
    try:
        result = rebate_engine.execute(query, {"criteria": criteria}).fetchone()
        if result:
            logging.info(f"Rebate amount found: {result['amount']}")
            return jsonify({"rebate_amount": result["amount"]}), 200
        else:
            logging.warning("Rebate not found")
            return jsonify({"error": "Rebate not found"}), 404
    except Exception as e:
        logging.error(f"Error executing query: {e}")
        return jsonify({"error": "Database error"}), 500

@app.route("/get-rebate-details", methods=["POST"])
def get_rebate_details():
    """Fetch applicable rebate details."""
    data = request.json

    # Validate input
    age = data.get("age")
    financial_year = data.get("financial_year")
    if not all([age, financial_year]):
        return jsonify({"error": "Age and financial year are required"}), 400

    try:
        # Determine age group
        if age <= 64:
            age_group = "Primary"
        elif 65 <= age <= 74:
            age_group = "Secondary"
        else:
            age_group = "Tertiary"

        # Query rebate_table
        query = text("SELECT * FROM rebate_table WHERE age_group = :age_group AND financial_year = :year")
        row = rebate_engine.execute(query, {"age_group": age_group, "year": financial_year}).fetchone()

        if row:
            return jsonify({"rebate_amount": row["rebate_amount"]}), 200
        else:
            return jsonify({"error": "No matching rebate found"}), 404

    except Exception as e:
        logging.error(f"Error in /get-rebate-details: {e}")
        return jsonify({"error": "Database error"}), 500

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "OK"}), 200

if __name__ == "__main__":
    logging.info("Starting Flask app")
    app.run(host="0.0.0.0", port=5001)