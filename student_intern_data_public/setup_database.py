import sqlite3

# Create a connection to the database
conn = sqlite3.connect('student_intern_data.db')

# Create a cursor object to execute SQL queries
cursor = conn.cursor()

# Create the Student table with auto-incrementing intern_id
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

# Commit the changes and close the connection
conn.commit()
conn.close()
