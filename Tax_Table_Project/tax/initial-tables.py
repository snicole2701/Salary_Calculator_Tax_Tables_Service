from sqlalchemy import create_engine, Column, Integer, Float, Date, MetaData, Table
from datetime import datetime

# Database connection
engine = create_engine('sqlite:///tax_database.db')  # Connect to (or create) the database
metadata = MetaData()

def create_and_populate_table(table_name, effective_date, end_date, tax_data):
    """
    Creates and populates a table in the database.
    Args:
        table_name (str): The name of the table to create.
        effective_date (datetime.date): The effective date of the data.
        end_date (datetime.date): The end date of the data.
        tax_data (list): The data to populate the table with.
    """
    # Define table schema
    table = Table(
        table_name, metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('min_income', Integer),
        Column('max_income', Integer),
        Column('tax_on_previous_bracket', Float),
        Column('tax_percentage', Float),
        Column('effective_date', Date),
        Column('end_date', Date)
    )

    # Create the table in the database
    metadata.create_all(engine)
    print(f"Table '{table_name}' created successfully!")

    # Add effective_date and end_date to each row in tax_data
    for entry in tax_data:
        entry['effective_date'] = effective_date
        entry['end_date'] = end_date

    # Populate the table with data
    with engine.connect() as conn:
        with conn.begin():  # Begin a transaction
            conn.execute(table.insert(), tax_data)
            print(f"Data committed into '{table_name}' successfully!")

if __name__ == "__main__":
    # Shared Tax Bracket Data for All Tables
    tax_data = [
        {'min_income': 1, 'max_income': 237100, 'tax_on_previous_bracket': 0, 'tax_percentage': 18},
        {'min_income': 237101, 'max_income': 370500, 'tax_on_previous_bracket': 42678, 'tax_percentage': 26},
        {'min_income': 370501, 'max_income': 512800, 'tax_on_previous_bracket': 77362, 'tax_percentage': 31},
        {'min_income': 512801, 'max_income': 673000, 'tax_on_previous_bracket': 121475, 'tax_percentage': 36},
        {'min_income': 673001, 'max_income': 857900, 'tax_on_previous_bracket': 179147, 'tax_percentage': 39},
        {'min_income': 857901, 'max_income': 1817000, 'tax_on_previous_bracket': 251258, 'tax_percentage': 41},
        {'min_income': 1817001, 'max_income': 9999999999, 'tax_on_previous_bracket': 644489, 'tax_percentage': 45},
    ]

    # Table 1: tax_period_2024
    create_and_populate_table(
        table_name='tax_period_2024',
        effective_date=datetime.strptime('2023-03-01', '%Y-%m-%d').date(),
        end_date=datetime.strptime('2024-02-28', '%Y-%m-%d').date(),
        tax_data=tax_data
    )

    # Table 2: tax_period_2025
    create_and_populate_table(
        table_name='tax_period_2025',
        effective_date=datetime.strptime('2024-03-01', '%Y-%m-%d').date(),
        end_date=datetime.strptime('2025-02-28', '%Y-%m-%d').date(),
        tax_data=tax_data
    )

    # Table 3: tax_period_2026
    create_and_populate_table(
        table_name='tax_period_2026',
        effective_date=datetime.strptime('2025-03-01', '%Y-%m-%d').date(),
        end_date=datetime.strptime('2026-02-28', '%Y-%m-%d').date(),
        tax_data=tax_data
    )