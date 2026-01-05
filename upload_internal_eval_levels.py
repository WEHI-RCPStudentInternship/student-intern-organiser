import sqlite3
import csv

# Connect to the SQLite database
conn = sqlite3.connect('student_intern.db')
cursor = conn.cursor()

# Create the Internal_eval_levels table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Internal_eval_levels (
        id INTEGER PRIMARY KEY,
        name TEXT
    )
''')

# Read level descriptions from the TSV file
with open('internal_eval_levels.tsv', 'r') as file:
    tsv_data = csv.reader(file, delimiter='\t')
    for row in tsv_data:
        level_name = row[0]
        cursor.execute('INSERT INTO Internal_eval_levels (name) VALUES (?)', (level_name,))

# Commit the changes and close the database connection
conn.commit()
conn.close()

print("Internal evaluation levels descriptions have been uploaded to the database.")