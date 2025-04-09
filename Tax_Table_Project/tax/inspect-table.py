import sqlite3

# Connect to the tax database
connection = sqlite3.connect('tax_database.db', isolation_level=None)  # Open in exclusive mode
cursor = connection.cursor()

# List all tables in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in the database:")
for table in tables:
    print(table[0])

# Inspect each table
for table in tables:
    table_name = table[0]
    print(f"\nInspecting '{table_name}':")

    # Check the schema of the table
    cursor.execute(f"PRAGMA table_info({table_name});")
    schema = cursor.fetchall()
    print("Schema:")
    for column in schema:
        print(f"  Column: {column[1]}, Type: {column[2]}")

    # Count rows in the table
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    row_count = cursor.fetchone()[0]
    print(f"Number of rows: {row_count}")

    # Fetch and display all rows if present
    if row_count > 0:
        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()
        print("Rows:")
        for row in rows:
            print(row)
    else:
        print("No rows found.")

# Close the connection
connection.close()