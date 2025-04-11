from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Float, Date
from datetime import datetime

# Database connection
engine = create_engine('sqlite:///app/databases/tax_database.db')  # Ensure the path to your database file is correct
metadata = MetaData()

def create_and_populate_future_table(table_name, effective_date, end_date, tax_data):
    """
    Creates and populates a new table in the database.
    Args:
        table_name (str): The name of the table to create (e.g., tax_period_<year>).
        effective_date (datetime.date): The effective date for the table.
        end_date (datetime.date): The end date for the table.
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

    # Insert data into the table
    with engine.connect() as conn:
        with conn.begin():  # Begin a transaction
            conn.execute(table.insert(), tax_data)
            print(f"Data committed into '{table_name}' successfully!")

if __name__ == "__main__":
    # Update the following values before running the script:
    newest_year = 2027  # Update to the desired year
    effective_date = datetime.strptime(f"{newest_year - 1}-03-01", "%Y-%m-%d").date()
    end_date = datetime.strptime(f"{newest_year}-02-28", "%Y-%m-%d").date()
    table_name = f"tax_period_{newest_year}"  # Dynamic table name based on the year

    # Tax bracket data: Update the values as needed
    tax_data = [
        {'min_income': 1, 'max_income': 237100, 'tax_on_previous_bracket': 0, 'tax_percentage': 18},
        {'min_income': 237101, 'max_income': 370500, 'tax_on_previous_bracket': 42678, 'tax_percentage': 26},
        {'min_income': 370501, 'max_income': 512800, 'tax_on_previous_bracket': 77362, 'tax_percentage': 31},
        {'min_income': 512801, 'max_income': 673000, 'tax_on_previous_bracket': 121475, 'tax_percentage': 36},
        {'min_income': 673001, 'max_income': 857900, 'tax_on_previous_bracket': 179147, 'tax_percentage': 39},
        {'min_income': 857901, 'max_income': 1817000, 'tax_on_previous_bracket': 251258, 'tax_percentage': 41},
        {'min_income': 1817001, 'max_income': 9999999999, 'tax_on_previous_bracket': 644489, 'tax_percentage': 45},
    ]

    # Create and populate the new table
    create_and_populate_future_table(
        table_name=table_name,
        effective_date=effective_date,
        end_date=end_date,
        tax_data=tax_data
    )