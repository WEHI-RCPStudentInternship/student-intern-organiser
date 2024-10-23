import sqlite3
import csv

# Connect to the SQLite database
conn = sqlite3.connect('student_intern_data.db')
cursor = conn.cursor()

# Create the Student table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Students (
        intern_id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        pronouns TEXT,
        status TEXT,
        email TEXT,
        mobile TEXT,
        course TEXT,
        course_major TEXT,
        link_to_application_doc TEXT,
        read_student_handbook TEXT,
        read_student_projects TEXT,
        cover_letter_projects TEXT,
        cover_letter_concept TEXT,
        cover_letter_technical TEXT,
        pronunciation TEXT,
        project TEXT,
        start_date DATE,
        end_date DATE,
        hours_per_week INTEGER,
        intake TEXT,
        supervisor_email TEXT,
        wehi_email TEXT,
        summary_tech_skills TEXT,
        summary_experience TEXT,
        summary_interest_in_projects TEXT,
        pre_internship_summary_recommendation_external TEXT,
        pre_internship_summary_recommendation_internal TEXT,
        pre_internship_technical_rating TEXT,
        pre_internship_social_rating TEXT,
        pre_internship_learning_quickly TEXT,
        pre_internship_enthusiasm TEXT,
        pre_internship_experience TEXT,
        pre_internship_communication TEXT,
        pre_internship_adaptable TEXT,
        pre_internship_problem_solver TEXT,
        post_internship_comments TEXT,
        post_internship_adaptability TEXT,
        post_internship_learn_technical TEXT,
        post_internship_learn_conceptual TEXT,
        post_internship_collaborative TEXT,
        post_internship_ambiguity TEXT,
        post_internship_complexity TEXT,
        post_internship_summary_rating_internal TEXT,
        post_internship_summary_rating_external TEXT
    )
''')

# Read data from the CSV file and insert into the database
with open('students.csv', 'r') as file:
    csv_data = csv.reader(file)
    next(csv_data)  # Skip the header row
    for row in csv_data:
        cursor.execute('INSERT INTO Students (full_name, pronouns, status, email, mobile, course, course_major, link_to_application_doc, read_student_handbook, read_student_projects, cover_letter_projects, cover_letter_concept, cover_letter_technical, pronunciation, project, start_date, end_date, hours_per_week, intake, supervisor_email, wehi_email, summary_tech_skills, summary_experience, summary_interest_in_projects, pre_internship_summary_recommendation_external, pre_internship_summary_recommendation_internal, pre_internship_technical_rating, pre_internship_social_rating, pre_internship_learning_quickly, pre_internship_enthusiasm, pre_internship_experience, pre_internship_communication, pre_internship_adaptable, pre_internship_problem_solver, post_internship_comments, post_internship_adaptability, post_internship_learn_technical, post_internship_learn_conceptual, post_internship_collaborative, post_internship_ambiguity, post_internship_complexity, post_internship_summary_rating_internal, post_internship_summary_rating_external) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?)',
                       row[:43])  # Limit the number of values to match the number of columns

# Commit the changes and close the database connection
conn.commit()
conn.close()

print("Data has been uploaded to the database.")

