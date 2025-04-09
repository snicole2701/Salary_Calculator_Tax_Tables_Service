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
- Provides a welcome message indicating the service is available

Get Tax Rate (POST/get-tax-rate):
- Retrieves the applicable tax information for the given income, age and period

Get Rebate (POST/get-rebate):
- Retrieves rebateinformation for given age and period

Health Checks (Get/health):
- Confirms the service is operational by returning a status message

## Key Features
Data Provider:
This service does not perform calculations. Instead, it provides structured tax and rebate data, which will be utilized by downstream microservices like Microservice 3.

Scalability:
- Designed for future expansion — updating the tax and rebate tables requires minimal effort.

Environment Variables:
- Database connectivity is managed using the following environment variables:
- TAX_BD_URI
- REBATE_DB_URI

Logging and Debugging:
Comprehensive logging helps monitor service interactions and debug any issues effectively.

## Deployment
Containerization:
This microservice is containerized using Podman. The container runs on a lightweight Python:3.9-slim image.

Hosting:
The container is deployed on Render, where environment variables are configured for database connections.

## Future Integration
The data provided by this service will be consumed by Microservice 3, which is currently under development, to perform detailed tax and rebate calculations based on user inputs.



