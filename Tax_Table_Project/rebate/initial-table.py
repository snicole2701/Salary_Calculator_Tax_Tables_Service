from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float

# Database connection
engine = create_engine('sqlite:///rebate_database.db')  # Connect to (or create) the database
metadata = MetaData()

# Define the rebate table schema
rebate_table = Table(
    'rebate_table', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('age_group', String),
    Column('year', Integer),
    Column('rebate_amount', Float)
)

def create_and_populate_rebate_table():
    # Create the table in the database
    metadata.create_all(engine)
    print("Table 'rebate_table' created successfully!")

    # Data to populate the rebate table
    rebate_data = [
        {'age_group': 'Primary', 'year': 2024, 'rebate_amount': 17235},
        {'age_group': 'Primary', 'year': 2025, 'rebate_amount': 17235},
        {'age_group': 'Primary', 'year': 2026, 'rebate_amount': 17235},
        {'age_group': 'Secondary (65 and older)', 'year': 2024, 'rebate_amount': 9444},
        {'age_group': 'Secondary (65 and older)', 'year': 2025, 'rebate_amount': 9444},
        {'age_group': 'Secondary (65 and older)', 'year': 2026, 'rebate_amount': 9444},
        {'age_group': 'Tertiary (75 and older)', 'year': 2024, 'rebate_amount': 3145},
        {'age_group': 'Tertiary (75 and older)', 'year': 2025, 'rebate_amount': 3145},
        {'age_group': 'Tertiary (75 and older)', 'year': 2026, 'rebate_amount': 3145},
    ]

    # Insert data into the table with explicit transaction handling
    with engine.connect() as conn:
        with conn.begin():
            conn.execute(rebate_table.insert(), rebate_data)
            print("Data committed successfully!")

    # Verify data insertion
    with engine.connect() as conn:
        result = conn.execute(rebate_table.select()).fetchall()
        print("Inserted Rows:", result)

if __name__ == "__main__":
    create_and_populate_rebate_table()