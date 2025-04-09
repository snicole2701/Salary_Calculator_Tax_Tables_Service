from sqlalchemy import create_engine, MetaData, Table

# Database connection
engine = create_engine('sqlite:///rebate_database.db')  # Ensure the path to your database file is correct
metadata = MetaData()

def add_future_rebates():
    # Reflect the existing rebate_table schema from the database
    rebate_table = Table('rebate_table', metadata, autoload_with=engine)
    
    # Placeholder for future rebate values
    new_rebate_data = [
        # Insert the correct values for the future financial year and rebate amounts for the specified age_group
        {'id': 10, 'age_group': 'Primary', 'year': 0000, 'rebate_amount': 000},
        {'id': 11, 'age_group': 'Secondary (65 and older)', 'year': 0000, 'rebate_amount': 000},
        {'id': 12, 'age_group': 'Tertiary (75 and older)', 'year': 0000, 'rebate_amount': 000},
    ]

    if not new_rebate_data:
        print("No new rebate data provided. Please update the script with new rows to add.")
        return

    # Insert new rows into the rebate_table
    with engine.connect() as conn:
        with conn.begin():  # Begin a transaction
            conn.execute(rebate_table.insert(), new_rebate_data)
            print(f"Added {len(new_rebate_data)} new rows to 'rebate_table' successfully!")

if __name__ == "__main__":
    # Call the function to add future rebates
    add_future_rebates()