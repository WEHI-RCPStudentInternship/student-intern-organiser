'''
The update_intake.py aims to update the INTAKE table in student_intern_data.db

We add new intake data to keep the information up-to-date

Change the status of previous intake from 'no' to 'finished'

For further updates, simply add new intakes and status to the intakes_data list

Author: [Yiyang Chen]
Date: [Sep, 2024]
'''

import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('student_intern_data.db')
cursor = conn.cursor()

# Step 1: Delete all existing rows from the Intakes table
cursor.execute('DELETE FROM Intakes')

# Step 2: Insert new rows into the Intakes table
intakes_data = [
    ('1 - Semester 2 2021', 'finished'),
    ('2 - Summer 2021/2022', 'finished'),
    ('3 - Semester 1 2022', 'finished'),
    ('4 - Semester 2 2022', 'finished'),
    ('5 - Summer 2022/2023', 'finished'),
    ('6 - Semester 1 2023', 'finished'),
    ('7 - Semester 2 2023', 'finished'),
    ('8 - Summer 2023/2024', 'finished'),
    ('9 - Semester 1 2024', 'finished'),
    ('10 - Semester 2 2024', 'current'),
    ('11 - Summer 2024/2025', 'new')
]

cursor.executemany('''
    INSERT INTO Intakes (name, status)
    VALUES (?, ?)
''', intakes_data)

# Commit changes and close the connection
conn.commit()
conn.close()

print("Intakes table has been cleared and updated.")
