import sqlite3
import csv

# Connect to the SQLite database
conn = sqlite3.connect('student_intern_data.db')
cursor = conn.cursor()

# Create the Statuses table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Statuses (
        id INTEGER PRIMARY KEY,
        name TEXT
    )
''')

# Read status names from the TSV file
with open('statuses.tsv', 'r') as file:
    tsv_data = csv.reader(file, delimiter='\t')
    for row in tsv_data:
        status_name = row[0]  # Assuming the status name is in the second column (index 1)
        cursor.execute('INSERT INTO Statuses (name) VALUES (?)', (status_name,))

# Commit the changes and close the database connection
conn.commit()
conn.close()

print("Statuses have been uploaded to the database.")

