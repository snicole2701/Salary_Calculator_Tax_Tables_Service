from sqlalchemy import create_engine, Column, Integer, Float, Date, MetaData, Table, String
from datetime import datetime

# Database connection
engine = create_engine('sqlite:///tax_database.db')  # Connect to (or create) the database
metadata = MetaData()

# Define the tax_table schema
tax_table = Table(
    'tax_table', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('table_name', String, nullable=False),  # Name of the related tax period table
    Column('financial_year', Integer, nullable=False),
    Column('effective_date', Date, nullable=False),
    Column('end_date', Date, nullable=False)
)

def create_tax_period_table(table_name, tax_data):
    """
    Creates and populates a tax period table in the database.
    Args:
        table_name (str): The name of the table to create.
        tax_data (list): The data to populate the table with.
    """
    # Define the tax period table schema
    table = Table(
        table_name, metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('min_income', Integer),
        Column('max_income', Integer),
        Column('tax_on_previous_bracket', Float),
        Column('tax_percentage', Float)
    )

    # Create the table
    metadata.create_all(engine)
    print(f"Table '{table_name}' created successfully!")

    # Populate the table with data
    with engine.connect() as conn:
        with conn.begin():  # Start a transaction
            conn.execute(table.insert(), tax_data)
            print(f"Data committed into '{table_name}' successfully!")

def create_and_populate_tax_table():
    """
    Creates and populates the tax_table with links to tax period tables and their metadata.
    """
    metadata.create_all(engine)  # Create the table
    print("Table 'tax_table' created successfully!")

    tax_periods = [
        {'table_name': 'tax_period_2024', 'financial_year': 2024,
         'effective_date': datetime.strptime('2023-03-01', '%Y-%m-%d').date(),
         'end_date': datetime.strptime('2024-02-28', '%Y-%m-%d').date()},
        {'table_name': 'tax_period_2025', 'financial_year': 2025,
         'effective_date': datetime.strptime('2024-03-01', '%Y-%m-%d').date(),
         'end_date': datetime.strptime('2025-02-28', '%Y-%m-%d').date()},
        {'table_name': 'tax_period_2026', 'financial_year': 2026,
         'effective_date': datetime.strptime('2025-03-01', '%Y-%m-%d').date(),
         'end_date': datetime.strptime('2026-02-28', '%Y-%m-%d').date()},
    ]

    # Insert tax period metadata into tax_table
    with engine.connect() as conn:
        with conn.begin():  # Start a transaction
            conn.execute(tax_table.insert(), tax_periods)
            print("Tax periods inserted into 'tax_table' successfully!")

if __name__ == "__main__":
    # Shared tax bracket data for all tax period tables
    tax_data = [
        {'min_income': 1, 'max_income': 237100, 'tax_on_previous_bracket': 0, 'tax_percentage': 18},
        {'min_income': 237101, 'max_income': 370500, 'tax_on_previous_bracket': 42678, 'tax_percentage': 26},
        {'min_income': 370501, 'max_income': 512800, 'tax_on_previous_bracket': 77362, 'tax_percentage': 31},
        {'min_income': 512801, 'max_income': 673000, 'tax_on_previous_bracket': 121475, 'tax_percentage': 36},
        {'min_income': 673001, 'max_income': 857900, 'tax_on_previous_bracket': 179147, 'tax_percentage': 39},
        {'min_income': 857901, 'max_income': 1817000, 'tax_on_previous_bracket': 251258, 'tax_percentage': 41},
        {'min_income': 1817001, 'max_income': 9999999999, 'tax_on_previous_bracket': 644489, 'tax_percentage': 45},
    ]

    # Create and populate individual tax period tables
    create_tax_period_table('tax_period_2024', tax_data)
    create_tax_period_table('tax_period_2025', tax_data)
    create_tax_period_table('tax_period_2026', tax_data)

    # Create and populate tax_table metadata
    create_and_populate_tax_table()