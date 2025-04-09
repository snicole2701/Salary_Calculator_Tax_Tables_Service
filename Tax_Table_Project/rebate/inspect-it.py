import sqlite3

# Connect to the rebate database
connection = sqlite3.connect('rebate_database.db', isolation_level=None)  # Open in exclusive mode
cursor = connection.cursor()

# List all tables in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in the database:")
for table in tables:
    print(table[0])

# Check the schema of rebate_table
cursor.execute("PRAGMA table_info(rebate_table);")
schema = cursor.fetchall()
print("\nSchema of rebate_table:")
for column in schema:
    print(f"Column: {column[1]}, Type: {column[2]}")

# Count rows in the table
cursor.execute("SELECT COUNT(*) FROM rebate_table;")
row_count = cursor.fetchone()[0]
print(f"Number of rows in rebate_table: {row_count}")

# Fetch and display all rows
if row_count > 0:
    cursor.execute("SELECT * FROM rebate_table;")
    rows = cursor.fetchall()
    print("\nRows in rebate_table:")
    for row in rows:
        print(row)
else:
    print("No rows found in rebate_table.")

# Close the connection
connection.close()