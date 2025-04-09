# Salary Calculator - Tax Tables Service

## Overview
The Tax Tables Service is a Flask-based microservice designed to store and provide tax and rebate information. This service acts as a data repository, utilizing user input to query pre-stored tables for relevant data. The retrieved information will be used in conjunction with the upcoming Microservice 3 to perform calculations. The data was sourced directly from the SARS website, cleaned, and stored in SQLite databases to ensure accuracy and maintainability.

This service focuses solely on storing, retrieving, and serving tax and rebate data via APIs, providing a robust foundation for downstream microservices that will handle the calculations.

## Data Preparation
Web Scraping:
- Tax and rebate tables were scraped directly from the SARS website.
- The extracted data included income thresholds, tax rates, and rebate criteria.

Data Cleaning:
  - Ensured all information was accurate, well-structured, and formatted for database insertion.

Database Automation:
  - Future-proof scripts were created to enable easy updates to the tax and rebate tables. New values can simply be added to the scripts, and the databases will be updated with minimal manual effort.

## Endpoints
Home (GET /):
- Provides a welcome message, confirming that the Tax Tables Service is available and operational.

Get Tax Rate (POST /get-tax-rate):
- Retrieves the tax rate for a given income threshold.
- Parameters:- income (float): The income value for which the tax rate is to be retrieved.

Get Tax Details (POST /get-tax-details):
- Dynamically queries the tax tables based on user input to retrieve detailed tax information.
- Parameters:- month (int): The month to determine the applicable tax period.
- year (int): The year to determine the financial year.
- income (float): The income value for which tax details are to be retrieved.

Get Rebate (POST /get-rebate):
- Fetches the rebate amount based on specific criteria.
- Parameters:
- criteria (string): The eligibility criteria for the rebate.

Get Rebate Details (POST /get-rebate-details):
- Dynamically queries the rebate tables based on user input to retrieve detailed rebate information.
- Parameters:- age (int): The user's age to determine the rebate group.
- financial_year (int): The financial year for which rebate details are to be retrieved.

Health Checks (GET /health):
- Confirms the service's health and readiness by returning a status message.


## Key Features
Data Management:
- Stores, manages, and queries tax and rebate tables efficiently.
- Provides structured tax and rebate data for downstream calculations in Microservice 3.

Scalability:
- Designed for future expansion — tax and rebate tables can be updated with minimal effort via automation scripts.

Dynamic Querying:
- Dynamically queries tax and rebate tables based on user inputs, ensuring that the data served is accurate and relevant.

Environment Variables:
- Database connectivity is managed using the following environment variables:
- TAX_DB_URI
- REBATE_DB_URI

Logging and Debugging:
- Comprehensive logging helps monitor interactions and debug issues effectively.



## Deployment
Containerization:
- The microservice is containerized using Podman.
- It runs on a lightweight Python:3.9-slim image, ensuring efficient resource usage.

Hosting:
- Deployed on Render, where environment variables are configured for secure database connectivity.



## Future Integration
The data provided by this service will be consumed by Microservice 3, enabling it to perform detailed tax and rebate calculations based on user inputs retrieved from Microservice 1. This integration creates a seamless workflow across all services in the Salary Calculator project.

