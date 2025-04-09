from flask import Flask, request, jsonify
from sqlalchemy import create_engine, text
import os
import logging

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

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "OK"}), 200

if __name__ == "__main__":
    logging.info("Starting Flask app")
    app.run(host="0.0.0.0", port=5001)