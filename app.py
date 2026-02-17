import csv
import os
import shutil
import sqlite3
import traceback
import zipfile
from collections import Counter
from datetime import datetime, timedelta
from urllib.parse import unquote

from flask import (Flask, jsonify, redirect, render_template, request, Response,
                   send_file, url_for)
import traceback

import import_csv_from_redcap

app = Flask(__name__)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 300

 # Replace with your SQLite database file path
db_path = 'student_intern_data/student_intern_data.db'
print("CWD =", os.getcwd())
print("DB PATH (relative) =", db_path)
print("DB PATH (absolute) =", os.path.abspath(db_path))

import io

# NOTE:
# Students.project is deprecated.
# Always use Students.project_id + JOIN Projects.


def fetch_students_with_project_name(cursor, where_sql="", params=(), order_sql=""):
    query = f"""
        SELECT
            s.intern_id,
            s.full_name,
            s.email,
            s.pronunciation,
            p.name AS project,
            s.intake,
            s.course,
            s.status,
            s.post_internship_summary_rating_internal,
            s.pronouns,
            s.pre_internship_summary_recommendation_internal,
            s.show_key_skill,
            s.mobile
        FROM Students s
        LEFT JOIN Projects p ON s.project_id = p.id
        {where_sql}
        {order_sql}
    """
    cursor.execute(query, params)
    return cursor.fetchall()


def filter_students(status_of_students_to_filter,title,context = None):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Projects')
    projects = cursor.fetchall()


    cursor.execute('SELECT id FROM Intakes where status  = "new"')
    intake_current = cursor.fetchall()[0][0]


    # Retrieve student data from the database
    cursor.execute('SELECT * FROM Statuses')
    statuses = cursor.fetchall()

    current_statuses_list = [row[0] for row in statuses if row[0] in status_of_students_to_filter]

    # Retrieve student data from the database
    # Prepare the SQL query with a placeholder for the statuses filter
        # Build placeholders for status ids
    status_placeholders = ",".join(["?"] * len(current_statuses_list))

    base_query = f"""
        SELECT
            s.intern_id,
            s.full_name,
            s.email,
            s.pronunciation,
            p.name AS project,
            i.name AS intake,
            s.course,
            st.name AS status,
            s.post_internship_summary_rating_internal,
            s.pronouns,
            CAST(COALESCE(s.pre_internship_internal_eval_level_id, '') AS TEXT) || ' ' || COALESCE(lvl.name, ''),
            s.show_key_skill,
            s.mobile
        FROM Students s
        LEFT JOIN Projects p ON s.project_id = p.id
        LEFT JOIN Intakes  i ON s.intake_id  = i.id
        LEFT JOIN Statuses st ON s.status_id = st.id
        LEFT JOIN internal_eval_levels lvl ON s.pre_internship_internal_eval_level_id = lvl.id
        WHERE s.intake_id = ?
          AND s.status_id IN ({status_placeholders})
    """

    params = [intake_current] + current_statuses_list

    if context == "missed_out":
        base_query += """
          AND s.pre_internship_internal_eval_level_id = 8
        """

    base_query += " ORDER BY st.name ASC"

    cursor.execute(base_query, params)
    students = cursor.fetchall()


    # Close the database connection
    conn.close()
    title_of_page = title
    return render_template('index.html', students=students,statuses=statuses,title_of_page=title_of_page,projects=projects)

def get_empty_users(condition):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = f"SELECT * FROM students WHERE {condition} IS NULL OR {condition} NOT LIKE '%@wehi.edu.au%' "
    cursor.execute(query)
    users = cursor.fetchall()
    conn.close()
    return users

@app.route('/menu_page',methods=['GET'])
def menu_page():
    return render_template('menu_page.html')

@app.route('/current_student')
def current_student():
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Retrieve current student statuses and projects
    cursor.execute('SELECT * FROM Statuses')
    statuses = cursor.fetchall()

    cursor.execute('SELECT * FROM Projects')
    projects = cursor.fetchall()

    cursor.execute('SELECT id FROM Intakes where status  = "current"')
    intake_current = cursor.fetchall()[0][0]

    # Define current student status IDs
    status_of_students_current = [10, 11, 12, 13]

    # Retrieve current students with specific status
    placeholder = ','.join(['?'] * len(status_of_students_current))
    query = '''
        SELECT s.intern_id, s.full_name, s.email, s.pronunciation, p.name, i.name AS intake, s.course, st.name, s.post_internship_summary_rating_internal, s.pronouns, CAST(COALESCE(s.pre_internship_internal_eval_level_id, '') AS TEXT) || ' ' || COALESCE(lvl.name, ''), s.show_key_skill, s.mobile, s.github_username
        FROM Students s
        LEFT JOIN Statuses st ON s.status_id = st.id
        LEFT JOIN Intakes i ON s.intake_id = i.id
        LEFT JOIN Projects p ON s.project_id = p.id
        LEFT JOIN internal_eval_levels lvl ON s.pre_internship_internal_eval_level_id = lvl.id
        WHERE s.intake_id = ? AND s.status_id IN ({}) ORDER BY st.id ASC
    '''.format(','.join(['?'] * len(status_of_students_current)))


    # Execute the query with the statuses list
    cursor.execute(query, [intake_current] + status_of_students_current)
    students = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Title for the page

    # Render the HTML page with all data
    return render_template('current_empty_email.html', students=students, statuses=statuses, projects=projects, empty_email_users=students)


@app.route('/download_empty_emails')
def download_empty_emails():
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Retrieve current student statuses and projects
    cursor.execute('SELECT * FROM Statuses')
    statuses = cursor.fetchall()

    cursor.execute('SELECT * FROM Projects')
    projects = cursor.fetchall()

    cursor.execute('SELECT id FROM Intakes where status  = "current"')
    intake_current = cursor.fetchall()[0][0]

    # Define current student status IDs
    status_of_students_current = [10, 11, 12, 13]
    status_id_list = [row[0] for row in statuses if row[0] in status_of_students_current] 
    # Retrieve current students with specific status
    placeholder = ','.join(['?'] * len(status_id_list))
    query = f'''
        SELECT
            s.intern_id, s.full_name, s.email, s.pronunciation, p.name, i.name AS intake, s.course,
            st.name AS status, s.post_internship_summary_rating_internal,s.pronouns, 
            CAST(COALESCE(s.pre_internship_internal_eval_level_id, '') AS TEXT) || ' ' || COALESCE(lvl.name, ''), s.wehi_email, s.mobile, s.github_username
        FROM Students s 
        LEFT JOIN Projects ON s.project_id = p.id
        LEFT JOIN internal_eval_levels lvl ON s.pre_internship_internal_eval_level_id = lvl.id
        LEFT JOIN Intakes i ON s.intake_id = i.id
        LEFT JOIN Statuses st ON s.status_id = st.id
        WHERE s.intake_id = ?
        AND s.status_id IN ({placeholder})
        AND (s.wehi_email IS NULL OR s.wehi_email NOT LIKE '%@wehi.edu.au%')
        ORDER BY st.name ASC
    '''.format(','.join(['?'] * len(status_id_list)))


    # Execute the query with the statuses list
    cursor.execute(query, [intake_current] + status_id_list)
    empty_email_users = cursor.fetchall()
    selected_columns = [ (user[0], user[1], user[2], '') for user in empty_email_users ]
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['User ID', 'Name', 'Email', 'WEHI_Email'])
    cw.writerows(selected_columns)

    output = si.getvalue()
    si.close()

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=empty_email_users.csv"})

def update_students_by_criteria(criteria, update_fields):
    # Check if criteria and update_fields are not empty
    if not criteria or not update_fields:
        return "Criteria and update fields cannot be empty."

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Constructing the WHERE part of the SQL query from criteria
        criteria_query_parts = [f"{key} = ?" for key in criteria.keys()]
        criteria_query = " AND ".join(criteria_query_parts)

        # Constructing the SET part of the SQL query from update_fields
        update_query_parts = [f"{key} = ?" for key in update_fields.keys()]
        update_query = ", ".join(update_query_parts)

        # Constructing the complete SQL query
        sql_query = f"UPDATE Students SET {update_query} WHERE {criteria_query}"

        # Executing the query
        cursor.execute(sql_query, list(update_fields.values()) + list(criteria.values()))
        conn.commit()

        if cursor.rowcount == 0:
            print("No rows were updated. Please check your criteria.")
            return
        else:
            print(f"Successfully updated {cursor.rowcount} row(s).")
            return

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return
    finally:
        if conn:
            conn.close()


def update_email(csv_path):
    with open(csv_path, mode='r', encoding='Windows-1252') as file:
        csv_reader = csv.reader(file)
        # Skip the header
        next(csv_reader, None)
        # Read the data into a list of tuples
        data_list = [(row[0], row[1], row[2], row[3]) for row in csv_reader]
    
    print(data_list)
    
    for student_id, student_name, student_email, wehi_email in data_list:
        criteria = {"intern_id": student_id, "email": student_email, "full_name":student_name}
        update_fields = {"wehi_email": wehi_email}
        update_students_by_criteria(criteria, update_fields)


@app.route('/update_wehi',methods=['GET', 'POST'])
def update_wehi():
    if request.method == 'POST':
        if 'csv_file' in request.files:
            file = request.files['csv_file']
            if file and file.filename != '':
                filename = file.filename
                filepath = 'student_intern_data/attachments/' + filename
                file.save(filepath)
                update_email(filepath)
            else:
                pass
        else:
            pass
    return render_template('update_wehi.html')

@app.route('/github_username')
def add_to_github():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Projects')
    projects = cursor.fetchall()

    cursor.execute('SELECT id FROM Intakes where status  = "current"')
    intake_current = cursor.fetchall()[0][0]


    # Retrieve student data from the database
    cursor.execute('SELECT * FROM Statuses')
    statuses = cursor.fetchall()

    status_of_students_to_filter = [10, 11, 12, 13]
    status_id_list = [row[0] for row in statuses if row[0] in status_of_students_to_filter]

    # Retrieve student data from the database
    # Prepare the SQL query with a placeholder for the statuses filter
    query = '''
        SELECT s.intern_id, s.full_name, s.email, s.pronunciation, p.name, i.name AS intake, 
        s.course, st.name AS status, s.post_internship_summary_rating_internal, s.pronouns,
        CAST(COALESCE(s.pre_internship_internal_eval_level_id, '') AS TEXT) || ' ' || COALESCE(lvl.name, ''), 
        s.wehi_email, s.mobile, s.github_username
        FROM Students s
        LEFT JOIN Intakes i ON s.intake_id = i.id
        LEFT JOIN Statuses st ON s.status_id = st.id
        LEFT JOIN Projects p ON s.project_id = p.id
        LEFT JOIN internal_eval_levels lvl ON s.pre_internship_internal_eval_level_id = lvl.id
        WHERE s.intake_id = ?
            AND s.status_id IN ({})
        ORDER BY st.name ASC
    '''.format(','.join(['?'] * len(status_id_list)))


    # Execute the query with the statuses list
    cursor.execute(query, [intake_current] + status_id_list)
    students = cursor.fetchall()


    # Close the database connection
    conn.close()
    title_of_page = "Github Username"
    return render_template('empty_github_username.html', students=students,statuses=statuses,title_of_page=title_of_page,projects=projects)



@app.errorhandler(Exception)
def handle_error(e):
    error_message = str(e) or "Unknown error occurred"
    return render_template('error_page.html', error_message=error_message), 500



@app.route('/new_applications')
def new_applications():
    statuses = [1]
    title = "New Intake Applications" 
    html_to_render = filter_students(statuses,title)
    return html_to_render

@app.route('/quick_review')
def quick_review():
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Projects')
    projects = cursor.fetchall()

    cursor.execute('SELECT id FROM Intakes where status  = "new"')
    intake_current = cursor.fetchall()[0][0]

    # Retrieve student data from the database
    cursor.execute('SELECT * FROM Statuses')
    statuses = cursor.fetchall()

    status_of_students_to_filter = [3]
    status_id_list = [row[0] for row in statuses if row[0] in status_of_students_to_filter]

    # Retrieve student data from the database
    # Prepare the SQL query with a placeholder for the statuses filter
    query = '''
        SELECT
            s.intern_id, s.full_name, s.email, s.pronunciation, p.name, i.name AS intake,
            s.course,st.name AS status, s.post_internship_summary_rating_internal, s.pronouns,
            CAST(COALESCE(s.pre_internship_internal_eval_level_id, '') AS TEXT) || ' ' || COALESCE(lvl.name, ''), 
            s.show_key_skill, s.mobile
        FROM Students s
        LEFT JOIN Intakes i ON s.intake_id = i.id
        LEFT JOIN Statuses st ON s.status_id = st.id
        LEFT JOIN Projects p ON s.project_id = p.id
        LEFT JOIN internal_eval_levels lvl ON s.pre_internship_internal_eval_level_id = lvl.id
        WHERE s.intake_id = ?
        AND s.status_id IN ({})
        ORDER BY st.name ASC
    '''.format(','.join(['?'] * len(status_id_list)))


    # Execute the query with the statuses list
    cursor.execute(query, [intake_current] + status_id_list)
    students = cursor.fetchall()

    # Close the database connection
    conn.close()
    title_of_page = "New Intake Quick Review"
    return render_template('index.html', students=students,statuses=statuses,title_of_page=title_of_page,projects=projects)

@app.route('/have_interviewed')
def have_interviewed():
    statuses = [6]
    title = "New Intake - Have Interviewed" 
    html_to_render = filter_students(statuses,title,"interview")
    return html_to_render

@app.route('/offered_accepted')
def offered_accepted():
    statuses = [7,8,9]
    title = "New Intake - Offered & Accepted" 
    html_to_render = filter_students(statuses,title,"interview")
    return html_to_render

@app.route('/email_ack')
def email_ack():
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()


    cursor.execute('SELECT * FROM Projects')
    projects = cursor.fetchall()

    cursor.execute('SELECT id FROM Intakes where status  = "new"')
    intake_current = cursor.fetchall()[0][0]


    # Retrieve student data from the database
    cursor.execute('SELECT * FROM Statuses')
    statuses = cursor.fetchall()

    status_of_students_to_filter = [2]
    status_id_list = [row[0] for row in statuses if row[0] in status_of_students_to_filter]

    # Retrieve student data from the database
    # Prepare the SQL query with a placeholder for the statuses filter
    query = '''
        SELECT
            s.intern_id, s.full_name, s.email, s.pronunciation, p.name, i.name AS intake,  s.course,
            st.name AS status, CAST(COALESCE(s.pre_internship_internal_eval_level_id, '') AS TEXT) || ' ' || COALESCE(lvl.name, ''), 
            s.pronouns, s.pre_internship_summary_recommendation_internal, s.show_key_skill, s.mobile
        FROM Students s
        LEFT JOIN Intakes i ON s.intake_id = i.id
        LEFT JOIN Statuses st ON s.status_id = st.id
        LEFT JOIN Projects p on s.project_id = p.id
        LEFT JOIN internal_eval_levels lvl ON s.pre_internship_internal_eval_level_id = lvl.id
        WHERE s.intake_id = ?
        AND s.status_id IN ({})
        ORDER BY st.name ASC
    '''.format(','.join(['?'] * len(status_id_list)))


    # Execute the query with the statuses list
    cursor.execute(query, [intake_current] + status_id_list)
    students = cursor.fetchall()


    # Close the database connection
    conn.close()
    title_of_page = "New Intake Email Acknowledgment"
    return render_template('index.html', students=students,statuses=statuses,title_of_page=title_of_page,projects=projects)

@app.route('/to_interview')
def to_interview():
    statuses = [5]
    title = "New Intake - Email to Interview" 
    html_to_render = filter_students(statuses,title,"interview")
    return html_to_render

@app.route('/on_waiting_list')
def on_waiting_list():
    statuses = [4]
    title = "New Intake - On Waiting List" 
    html_to_render = filter_students(statuses,title,"waiting_list")
    return html_to_render


@app.route('/missed_out')
def missed_out():
    statuses = [3]
    title = "New Intake - Missed Out On Waiting List" 
    html_to_render = filter_students(statuses,title,"missed_out")
    return html_to_render

@app.route('/email_intake/<int:intake_id>', methods=['GET'])
def email_intake(intake_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Intakes WHERE id = ?',(intake_id,))
    
    intake = cursor.fetchall()[0]
    intake_name = intake[1]
    intake_start_date = intake[5]

    # Retrieve student data from the database
    cursor.execute('SELECT * FROM Statuses')
    statuses = cursor.fetchall()

    status_of_students_to_filter = [10,11,12,13] # from quick review to Interviewed by non-RCP supervisor
    status_id_list= [row[0] for row in statuses if row[0] in status_of_students_to_filter]

    # Retrieve student data from the database
    # Prepare the SQL query with a placeholder for the statuses filter
    query = '''
        SELECT
            s.intern_id, s.full_name, s.email, s.course
        FROM Students s
        WHERE s.intake_id = ?
          AND s.status_id IN ({})
        '''.format(','.join(['?'] * len(status_id_list)))

    # Execute the query with the statuses list
    cursor.execute(query, [intake_id] + status_id_list)
    students = cursor.fetchall()
    
    # Collect all student emails in one list (no separation by course)
    all_student_emails = []
    for student in students:
        email = student[2]
        if email:  # Only add if email exists
            all_student_emails.append(email)

    # Join all emails into one comma-separated string
    student_emails_combined = ",".join(all_student_emails)

    # Get the intake start date and calculate Monday of that week
    intake_start_date_object = datetime.strptime(intake_start_date, '%Y-%m-%d').date()

    # Find the Monday of the week containing the start date
    days_since_monday = intake_start_date_object.weekday()  # Monday is 0, Sunday is 6
    start_monday = intake_start_date_object - timedelta(days=days_since_monday)

    # Get email schedule from database and calculate dates dynamically - ordered by week progression
    cursor.execute('SELECT id, intake_id, week_number, week_offset_days, subject, body FROM EmailSchedule WHERE intake_id = ? ORDER BY week_offset_days ASC', (intake_id,))
    table_rows = cursor.fetchall()
    
    # Convert to dict format for template with calculated dates
    email_schedule = []
    for row in table_rows:
        week_offset_days = row[3] if row[3] is not None else 0  # Get week_offset_days column
        calculated_date = start_monday + timedelta(days=week_offset_days)
        
        email_schedule.append({
            'id': row[0],           # id
            'intake_id': row[1],    # intake_id
            'week_number': row[2],  # week_number
            'date_for_interns': calculated_date.strftime('%Y-%m-%d'),
            'subject': row[4] if row[4] is not None else f'Week {row[2]} email',  # subject
            'body': row[5] if row[5] is not None else f'Email content for {row[2]}'  # body
        })

    conn.close()

    return render_template(
        'email_intake.html', 
        intake=intake, 
        intake_id=intake_id, 
        student_emails=student_emails_combined, 
        all_student_emails=all_student_emails,
        table_rows=email_schedule
        )

@app.route('/edit_email_template/<int:email_id>', methods=['GET', 'POST'])
def edit_email_template(email_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    if request.method == 'POST':
        # Handle form submission to update email template
        subject = request.form.get('subject')
        body = request.form.get('body')
        new_intake_start_date = request.form.get('intake_start_date')


        # Get current email data to check which week this is
        cursor.execute('SELECT id, intake_id, week_number, week_offset_days FROM EmailSchedule WHERE id = ?', (email_id,))
        email_data = cursor.fetchone()
        intake_id = email_data[1]
        
        # Update the email template
        cursor.execute('''UPDATE EmailSchedule 
                         SET subject = ?, body = ?, last_modified = CURRENT_DATE
                         WHERE id = ?''', (subject, body, email_id))
        
        # If intake start date is provided and this is week 1, update the intake start date and adjust all week dates
        if new_intake_start_date and email_data[2] == '1 - First week':
            # Update intake start date
            cursor.execute('''UPDATE Intakes 
                             SET intake_start_date = ?
                             WHERE id = ?''', (new_intake_start_date, intake_id))

            # Get all email schedule rows for this intake
            cursor.execute('SELECT id, week_offset_days FROM EmailSchedule WHERE intake_id = ?', (intake_id,))
            all_weeks = cursor.fetchall()

            # Calculate new start_monday from new_intake_start_date
            new_start_date_object = datetime.strptime(new_intake_start_date, '%Y-%m-%d').date()
            days_since_monday = new_start_date_object.weekday()
            new_start_monday = new_start_date_object - timedelta(days=days_since_monday)

            # Update all week dates in EmailSchedule
            for week_row in all_weeks:
                week_id = week_row[0]
                week_offset_days = week_row[1] if week_row[1] is not None else 0
                new_week_date = new_start_monday + timedelta(days=week_offset_days)
                # Optionally, store the calculated date in a new column if needed, or just recalculate for display
                # If you want to store, add a column to EmailSchedule, e.g. 'scheduled_date', and update here
                # Example: cursor.execute('UPDATE EmailSchedule SET scheduled_date = ? WHERE id = ?', (new_week_date.strftime('%Y-%m-%d'), week_id))
                # For now, just recalculate for display
        
        conn.commit()
        conn.close()
        
        return redirect(url_for('email_intake', intake_id=intake_id))
    
    # GET request - show the edit form
    cursor.execute('SELECT id, intake_id, week_number, week_offset_days, subject, body FROM EmailSchedule WHERE id = ?', (email_id,))
    email_data = cursor.fetchone()
    
    if not email_data:
        conn.close()
        return "Email template not found", 404
    
    # Get intake start date to calculate the display date
    cursor.execute('SELECT intake_start_date FROM Intakes WHERE id = ?', (email_data[1],))
    intake_start_date = cursor.fetchone()[0]
    conn.close()
    
    # Calculate the date dynamically
    intern_start_date_object = datetime.strptime(intake_start_date, '%Y-%m-%d').date()
    days_since_monday = intern_start_date_object.weekday()
    start_monday = intern_start_date_object - timedelta(days=days_since_monday)
    week_offset_days = email_data[3] if email_data[3] is not None else 0
    calculated_date = start_monday + timedelta(days=week_offset_days)
    
    # Check if this is the first week (allow editing intake start date)
    is_first_week = email_data[2] == '1 - First week'

    email_template = {
        'id': email_data[0],           # id
        'intake_id': email_data[1],    # intake_id
        'week_number': email_data[2],  # week_number
        'date_for_interns': calculated_date.strftime('%Y-%m-%d'),  # calculated date
        'intake_start_date': intake_start_date,  # original intake start date
        'is_first_week': is_first_week,  # whether this is first week
        'subject': email_data[4] if email_data[4] is not None else f'Week {email_data[2]} email',  # subject
        'body': email_data[5] if email_data[5] is not None else f'Email content for {email_data[2]}'  # body
    }
    
    return render_template('edit_email_template.html', email_template=email_template)

@app.route('/links/', methods=['GET'])
def links():
    return render_template('links.html')

@app.route('/assigned_projects/', methods=['GET', 'PUT'])
@app.route('/assigned_projects/<intake_type>', methods=['GET', 'PUT'])
def assigned_projects(intake_type=None):
    intake_type = intake_type or 'new'
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        if request.method == 'GET':
            # Fetch the projects from the Projects table
            cursor.execute('SELECT id, name, status FROM Projects ORDER BY status ASC, name ASC' )
            projects = cursor.fetchall()
            print(projects)

            cursor.execute('SELECT id FROM Intakes where status  = "'+intake_type+'"')
            intake_current = cursor.fetchall()[0][0]

            cursor.execute('''SELECT s.intern_id, s.full_name, p.name, s.pronouns, st.name, s.cover_letter_projects 
                            FROM Students s 
                            LEFT JOIN Statuses st ON s.status_id = st.id 
                            LEFT JOIN Projects p ON s.project_id = p.id
                            WHERE s.intake_id = ?''',(intake_current,))
            students = cursor.fetchall()

            cursor.execute('SELECT * FROM Statuses')
            statuses = {row[0]: row[1] for row in cursor.fetchall()}

            status_id_list = [3,4,5,6,7,8,9,10,11,12,13,14]

            # Retrieve student data from the database
            # Prepare the SQL query with a placeholder for the statuses filter
            query = '''
                SELECT
                    s.intern_id,
                    s.full_name,
                    s.project_id,
                    s.pronouns,
                    p.name, 
                    st.name AS status,
                    s.cover_letter_projects,
                    s.pre_internship_internal_eval_level_id,
                    COALESCE(lvl.name, ''),
                    s.course,
                    s.show_key_skill
                FROM Students s
                LEFT JOIN internal_eval_levels lvl ON s.pre_internship_internal_eval_level_id = lvl.id
                LEFT JOIN projects p ON s.project_id = p.id
                LEFT JOIN statuses st on s.status_id = st.id
                WHERE s.intake_id = ?
                AND s.status_id IN ({})
                ORDER BY s.status_id DESC, s.pre_internship_internal_eval_level_id ASC
            '''.format(','.join(['?'] * len(status_id_list)))


            # Execute the query with the statuses list
            cursor.execute(query, [intake_current] + status_id_list)
            students = cursor.fetchall()

            print(students)

            # Close the database connection
            cursor.close()
            conn.close()
            return render_template('Assigned_projects.html', projects=projects, students=students, statuses=statuses)
        elif request.method == 'PUT':
            # Handle the AJAX request for updating the student's project assignment
            data = request.get_json()
            intern_id = data['internId']
            new_project_id = data['projectId']

            # Update the student's project assignment in the database
            cursor.execute('UPDATE Students SET project_id = ? WHERE intern_id = ?', (new_project_id, intern_id))
            conn.commit()

            # Close the database connection
            cursor.close()
            conn.close()

            return jsonify({'status': 'success', 'message': 'Project assignment updated successfully'})

    except Exception as e:
        # Handle any errors
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Route to handle the AJAX request for updating the student's project assignment
@app.route('/update_project_assignment', methods=['PUT'])
def update_project_assignment():
    try:
        data = request.get_json()
        print("update_project_assignment payload:", data)

        intern_id = data['internId']
        new_project_id = data['projectId']

        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Update the student's project assignment in the database
        cursor.execute('UPDATE Students SET project_id = ? WHERE intern_id = ?', (new_project_id, intern_id))
        conn.commit()

        # Close the database connection
        cursor.close()
        conn.close()

        return jsonify({'status': 'success', 'message': 'Project assignment updated successfully'})

    except Exception as e:
        # Handle any errors
        return jsonify({'status': 'error', 'message': str(e)}), 500

#  Generic Pre Internship Evaluation Per Student
@app.route('/submit_student_evaluation', methods=['POST'])
def submit_student_evaluation():
    # Retrieve  data from the form
    student_id = request.form.get('intern_id')
    status = request.form.get('status')
    pronunciation = request.form.get('pronunciation')
    remote_internship = request.form.get('remote_internship')
    code_of_conduct = request.form.get('code_of_conduct')
    facilitator_follower = request.form.get('facilitator_follower')
    listener_or_talker = request.form.get('listener_or_talker')
    thinker_brainstormer = request.form.get('thinker_brainstormer')
    cover_letter_projects = request.form.get('cover_letter_projects')
    why_applied = request.form.get('why_applied')
    projects_recommended = request.form.get('projects_recommended')
    Overall_External = request.form.get('Overall_External')
    Overall_Internal = int(request.form.get('Overall_Internal'))
    learn_quickly_technical = request.form.get('learn_quickly_technical')
    learn_domain_concepts = request.form.get('learn_domain_concepts')
    Enthusiastic = request.form.get('Enthusiastic')
    Experience = request.form.get('Experience')
    Written_application = request.form.get('Written_Application')
    Phone_interview = request.form.get('Phone_Interview')
    show_key_skill = request.form.get('show_key_skill')
    #Communication = request.form.get('Written_Application')

    Adaptability = request.form.get('Adaptability')
    summary_tech_skills = request.form.get('summary_tech_skills')
    summary_experience = request.form.get('summary_experience')
    extra_notes = request.form.get('extra_notes')

    Communication = f"{Written_application} {Phone_interview}"
    print("---------")
    print(show_key_skill)
    print("---------")

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Update Students Evaluation data in the Students table
    cursor.execute('''
        UPDATE Students

        SET status_id = ?,
            pronunciation = ?,
            cover_letter_projects = ?,
            pre_internship_summary_recommendation_external = ?,
            pre_internship_internal_eval_level_id = ?,
            pre_internship_technical_rating = ?,
            pre_internship_learning_quickly = ?,
            pre_internship_enthusiasm = ?,
            pre_internship_experience = ?,
            pre_internship_communication = ?,
            pre_internship_adaptable = ?,
            summary_tech_skills = ?,
            extra_notes = ?,
            summary_experience = ?,
            remote_internship = ?,
            code_of_conduct = ?,
            facilitator_follower = ?,
            listener_or_talker = ?,
            thinker_brainstormer = ?,
            why_applied = ?,
            show_key_skill = ?,
            projects_recommended = ?

        WHERE intern_id = ?
    ''', (status,pronunciation, cover_letter_projects, Overall_External, Overall_Internal,learn_quickly_technical, learn_domain_concepts, Enthusiastic, Experience, Communication, Adaptability,  summary_tech_skills, extra_notes, summary_experience, remote_internship, code_of_conduct, facilitator_follower, listener_or_talker, thinker_brainstormer, why_applied, show_key_skill, projects_recommended, student_id))

    # Commit the changes and close the database connection
    conn.commit()
    conn.close()

    # Redirect to the student's evaluation  page in standardized vocabulary
    return redirect(url_for('pre_int_st_evaluation', intern_id=student_id))

@app.route('/pre_int_st_evaluation/<int:intern_id>', methods=['GET'])
def pre_int_st_evaluation(intern_id):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Retrieve the student's details from the database
    # query everything
    cursor.execute('''SELECT s.intern_id, s.full_name, s.pronouns, st.name, s.email, s.mobile, s.course, s.course_major, 
                s.link_to_application_doc, s.read_student_handbook, s.read_student_projects, s.cover_letter_projects, 
                s.cover_letter_concept, s.cover_letter_technical, s.pronunciation, p.name, s.start_date, s.end_date, 
                s.hours_per_week, i.name, s.supervisor_email, s.wehi_email, s.summary_tech_skills, s.summary_experience, 
                s.summary_interest_in_projects, s.pre_internship_summary_recommendation_external, 
                CAST(COALESCE(s.pre_internship_internal_eval_level_id, '') AS TEXT) || ' ' || COALESCE(lvl.name, ''), 
                s.pre_internship_technical_rating, s.pre_internship_social_rating, s.pre_internship_learning_quickly, 
                s.pre_internship_enthusiasm, s.pre_internship_experience, s.pre_internship_communication, 
                s.pre_internship_adaptable, s.pre_internship_problem_solver, s.post_internship_comments, 
                s.post_internship_adaptability, s.post_internship_learn_technical, s.post_internship_learn_conceptual, 
                s.post_internship_collaborative, s.post_internship_ambiguity, s.post_internship_complexity, 
                s.post_internship_summary_rating_internal, s.post_internship_summary_rating_external, s.github_username, 
                s.extra_notes, s.remote_internship, s.code_of_conduct, s.facilitator_follower, s.listener_or_talker, 
                s.thinker_brainstormer, s.why_applied, s.projects_recommended, s.redcap_id, s.show_key_skill 
                FROM Students s 
                LEFT JOIN Statuses st ON s.status_id = st.id
                LEFT JOIN Intakes i ON s.intake_id = i.id
                LEFT JOIN Projects p ON s.project_id = p.id
                LEFT JOIN internal_eval_levels lvl ON s.pre_internship_internal_eval_level_id = lvl.id
                WHERE s.intern_id = ?''', (intern_id,))
    student = cursor.fetchone()

    # Close the database connection
    conn.close()
    pronoun = str(student[3] or "")


    # Split the pronoun into multiple parts using the '/' delimiter
    #he/him/his or she/her or they/them/their
    try:
        pronoun_parts = pronoun.split('/')

        # Assign pronoun1, pronoun2, and pronoun3 based on the pronoun_parts
        pronoun1 = pronoun_parts[0].strip()
        pronoun2 = pronoun_parts[1].strip() if len(pronoun_parts) > 1 else ""
    except:
        pronoun1 = ""
        pronoun2 = ""
        print("error in pronoun splitting")

    # Find matching PDF files
    attachments_dir = 'student_intern_data/attachments'
    matching_files = []
    for filename in os.listdir(attachments_dir):
        if filename.startswith(str(intern_id)) and filename.lower().endswith('.pdf'):
            matching_files.append(filename)


    statuses = get_statuses()  # Retrieve the list of statuses from the database

    return render_template('pre_int_st_evaluation.html', student=student, pronoun1=pronoun1, pronoun2=pronoun2,statuses=statuses, matching_files=matching_files)

@app.route('/student_evaluation/<int:intern_id>', methods=['GET'])
def student_evaluation(intern_id):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Retrieve the feedback data from the Students table
    # query everything
    cursor.execute('''SELECT s.intern_id, s.full_name, s.pronouns, st.name, s.email, s.mobile, s.course, s.course_major, 
                s.link_to_application_doc, s.read_student_handbook, s.read_student_projects, s.cover_letter_projects, 
                s.cover_letter_concept, s.cover_letter_technical, s.pronunciation, p.name, s.start_date, s.end_date, 
                s.hours_per_week, i.name, s.supervisor_email, s.wehi_email, s.summary_tech_skills, s.summary_experience, 
                s.summary_interest_in_projects, s.pre_internship_summary_recommendation_external, 
                CAST(COALESCE(s.pre_internship_internal_eval_level_id, '') AS TEXT) || ' ' || COALESCE(lvl.name, ''), 
                s.pre_internship_technical_rating, s.pre_internship_social_rating, s.pre_internship_learning_quickly, 
                s.pre_internship_enthusiasm, s.pre_internship_experience, s.pre_internship_communication, 
                s.pre_internship_adaptable, s.pre_internship_problem_solver, s.post_internship_comments, 
                s.post_internship_adaptability, s.post_internship_learn_technical, s.post_internship_learn_conceptual, 
                s.post_internship_collaborative, s.post_internship_ambiguity, s.post_internship_complexity, 
                s.post_internship_summary_rating_internal, s.post_internship_summary_rating_external, s.github_username, 
                s.extra_notes, s.remote_internship, s.code_of_conduct, s.facilitator_follower, s.listener_or_talker, 
                s.thinker_brainstormer, s.why_applied, s.projects_recommended, s.redcap_id, s.show_key_skill 
                FROM Students s 
                LEFT JOIN Statuses st ON s.status_id = st.id
                LEFT JOIN Intakes i ON s.intake_id = i.id
                LEFT JOIN Projects p ON s.project_id = p.id
                LEFT JOIN internal_eval_levels lvl ON s.pre_internship_internal_eval_level_id = lvl.id
                ''')
    st_eval = cursor.fetchall()

    # Close the database connection
    conn.close()

    return render_template('student_evaluation.html', st_eval=st_eval)

#  Generic Post Internship Evaluation Per Student
# Submit Feedback Route
@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    # Retrieve the feedback data from the request form
    student_id = request.form.get('intern_id')
    adaptability = request.form.get('adaptability')
    learn_technical = request.form.get('learn_technical')
    learn_conceptual = request.form.get('learn_conceptual')
    collaborative = request.form.get('collaborative')
    ambiguity = request.form.get('ambiguity')
    complexity = request.form.get('complexity')
    my_reaction = request.form.get('my_reaction')

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Update the feedback data in the Students table
    cursor.execute('''
        UPDATE Students
        SET post_internship_adaptability = ?,
            post_internship_learn_technical = ?,
            post_internship_learn_conceptual = ?,
            post_internship_collaborative = ?,
            post_internship_ambiguity = ?,
            post_internship_complexity = ?,
            post_internship_summary_rating_external = ?
        WHERE intern_id = ?
    ''', (adaptability, learn_technical, learn_conceptual, collaborative, ambiguity, complexity, my_reaction, student_id))

    # Commit the changes and close the database connection
    conn.commit()
    conn.close()

    # Redirect to the student's details page
    return redirect(url_for('student', intern_id=student_id))
# feedback
@app.route('/feedback/<int:intern_id>', methods=['GET'])
def feedback(intern_id):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Retrieve the student's details from the database
    # query everything
    cursor.execute('''SELECT s.intern_id, s.full_name, s.pronouns, st.name, s.email, s.mobile, s.course, s.course_major, 
                s.link_to_application_doc, s.read_student_handbook, s.read_student_projects, s.cover_letter_projects, 
                s.cover_letter_concept, s.cover_letter_technical, s.pronunciation, p.name, s.start_date, s.end_date, 
                s.hours_per_week, i.name, s.supervisor_email, s.wehi_email, s.summary_tech_skills, s.summary_experience, 
                s.summary_interest_in_projects, s.pre_internship_summary_recommendation_external, 
                CAST(COALESCE(s.pre_internship_internal_eval_level_id, '') AS TEXT) || ' ' || COALESCE(lvl.name, ''), 
                s.pre_internship_technical_rating, s.pre_internship_social_rating, s.pre_internship_learning_quickly, 
                s.pre_internship_enthusiasm, s.pre_internship_experience, s.pre_internship_communication, 
                s.pre_internship_adaptable, s.pre_internship_problem_solver, s.post_internship_comments, 
                s.post_internship_adaptability, s.post_internship_learn_technical, s.post_internship_learn_conceptual, 
                s.post_internship_collaborative, s.post_internship_ambiguity, s.post_internship_complexity, 
                s.post_internship_summary_rating_internal, s.post_internship_summary_rating_external, s.github_username, 
                s.extra_notes, s.remote_internship, s.code_of_conduct, s.facilitator_follower, s.listener_or_talker, 
                s.thinker_brainstormer, s.why_applied, s.projects_recommended, s.redcap_id, s.show_key_skill 
                FROM Students s 
                LEFT JOIN Statuses st ON s.status_id = st.id
                LEFT JOIN Intakes i ON s.intake_id = i.id
                LEFT JOIN Projects p ON s.project_id = p.id
                LEFT JOIN internal_eval_levels lvl ON s.pre_internship_internal_eval_level_id = lvl.id
                WHERE s.intern_id = ?''', (intern_id,))
    student = cursor.fetchone()

    # Close the database connection
    conn.close()
    # Retrieve the pronoun from the database
    pronoun = str(student[2] or "")

    # Split the pronoun into multiple parts using the '/' delimiter
    pronoun_parts = pronoun.split('/')

    # Assign pronoun1, pronoun2 based on the pronoun_parts
    pronoun1 = pronoun_parts[0].strip()
    pronoun2 = pronoun_parts[1].strip() if len(pronoun_parts) > 1 else ""

    return render_template(
        'feedback.html',
        student=student,
        pronoun1=pronoun1,
        pronoun2=pronoun2
    )

@app.route('/feedback_table/<int:intern_id>', methods=['GET'])
def feedback_table(intern_id):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Retrieve the feedback data from the Students table
    # query everything
    cursor.execute('''SELECT s.intern_id, s.full_name, s.pronouns, st.name, s.email, s.mobile, s.course, s.course_major, 
                s.link_to_application_doc, s.read_student_handbook, s.read_student_projects, s.cover_letter_projects, 
                s.cover_letter_concept, s.cover_letter_technical, s.pronunciation, p.name, s.start_date, s.end_date, 
                s.hours_per_week, i.name, s.supervisor_email, s.wehi_email, s.summary_tech_skills, s.summary_experience, 
                s.summary_interest_in_projects, s.pre_internship_summary_recommendation_external, 
                CAST(COALESCE(s.pre_internship_internal_eval_level_id, '') AS TEXT) || ' ' || COALESCE(lvl.name, ''), 
                s.pre_internship_technical_rating, s.pre_internship_social_rating, s.pre_internship_learning_quickly, 
                s.pre_internship_enthusiasm, s.pre_internship_experience, s.pre_internship_communication, 
                s.pre_internship_adaptable, s.pre_internship_problem_solver, s.post_internship_comments, 
                s.post_internship_adaptability, s.post_internship_learn_technical, s.post_internship_learn_conceptual, 
                s.post_internship_collaborative, s.post_internship_ambiguity, s.post_internship_complexity, 
                s.post_internship_summary_rating_internal, s.post_internship_summary_rating_external, s.github_username, 
                s.extra_notes, s.remote_internship, s.code_of_conduct, s.facilitator_follower, s.listener_or_talker, 
                s.thinker_brainstormer, s.why_applied, s.projects_recommended, s.redcap_id, s.show_key_skill 
                FROM Students s 
                LEFT JOIN Statuses st ON s.status_id = st.id
                LEFT JOIN Intakes i ON s.intake_id = i.id
                LEFT JOIN Projects p ON s.project_id = p.id
                LEFT JOIN internal_eval_levels lvl ON s.pre_internship_internal_eval_level_id = lvl.id
                ''')
    students = cursor.fetchall()

    # Close the database connection
    conn.close()

    return render_template('feedback_table.html', students=students)


@app.route('/download_key_attributes')
def download_key_attributes():
    data = request.args.getlist('student_ids')
    values = data[0].split(',')
    student_ids = [int(value) for value in values]

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT s.full_name, s.pronunciation, p.name, st.name, s.mobile, s.email, 
                s.start_date, s.end_date, s.hours_per_week, s.pronouns, 
                CAST(COALESCE(s.pre_internship_internal_eval_level_id, '') AS TEXT) || ' ' || COALESCE(lvl.name, ''),
                i.name AS intake, s.course 
        FROM Students s 
        LEFT JOIN Statuses st ON s.status_id = st.id
        LEFT JOIN Intakes i ON s.intake_id = i.id
        LEFT JOIN Projects p ON s.project_id = p.id
        LEFT JOIN internal_eval_levels lvl ON s.pre_internship_internal_eval_level_id = lvl.id
        WHERE s.intern_id IN ({})
    '''.format(','.join('?' for _ in student_ids)), student_ids)

    students = cursor.fetchall()


    # Create a temporary directory to store the files
    temp_dir = 'student_intern_data/attachments/tmp'

    try:
        os.makedirs(temp_dir)
    except Exception:
        pass

    # Get the current datetime
    now = datetime.now()
    formatted_datetime = now.strftime("%Y-%m-%d-%H:%M:%S")

    # Create the CSV file inside the temporary directory
    csv_path = os.path.join(temp_dir, formatted_datetime+'_student_data.csv')
    with open(csv_path, 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Full Name', 'Pronunciation','Project','Status','Phone', 'Email', 'Start Date', 'End Date', 'Hours per Week','Pronouns','Summary pre-internship','Intake','Faculty'])


        for student in students:
            # Retrieve student data from the database
            # Write the student data to the CSV file
            csv_writer.writerow(student)


    return send_file(csv_path, as_attachment=True)


def get_statuses():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM Statuses')
    statuses = cursor.fetchall()
    conn.close()
    return statuses

def get_intakes():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM Intakes')
    intakes = cursor.fetchall()
    conn.close()
    return intakes

def get_all_intakes():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Intakes')
    intakes = [row for row in cursor.fetchall()]
    conn.close()
    return intakes

def get_all_projects():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM projects')
    projects = [row for row in cursor.fetchall()]
    conn.close()
    return projects

def get_projects():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM Projects')
    projects = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
    conn.close()
    return projects

def get_student_by_id(intern_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # query everything
    cursor.execute('''SELECT s.intern_id, s.full_name, s.pronouns, st.name, s.email, s.mobile, s.course, s.course_major, 
                s.link_to_application_doc, s.read_student_handbook, s.read_student_projects, s.cover_letter_projects, 
                s.cover_letter_concept, s.cover_letter_technical, s.pronunciation, p.name, s.start_date, s.end_date, 
                s.hours_per_week,s.intake_id, i.name, s.supervisor_email, s.wehi_email, s.summary_tech_skills, s.summary_experience, 
                s.summary_interest_in_projects, s.pre_internship_summary_recommendation_external, 
                CAST(COALESCE(s.pre_internship_internal_eval_level_id, '') AS TEXT) || ' ' || COALESCE(lvl.name, ''), 
                s.pre_internship_technical_rating, s.pre_internship_social_rating, s.pre_internship_learning_quickly, 
                s.pre_internship_enthusiasm, s.pre_internship_experience, s.pre_internship_communication, 
                s.pre_internship_adaptable, s.pre_internship_problem_solver, s.post_internship_comments, 
                s.post_internship_adaptability, s.post_internship_learn_technical, s.post_internship_learn_conceptual, 
                s.post_internship_collaborative, s.post_internship_ambiguity, s.post_internship_complexity, 
                s.post_internship_summary_rating_internal, s.post_internship_summary_rating_external, s.github_username, 
                s.extra_notes, s.remote_internship, s.code_of_conduct, s.facilitator_follower, s.listener_or_talker, 
                s.thinker_brainstormer, s.why_applied, s.projects_recommended, s.redcap_id, s.show_key_skill 
                FROM Students s 
                LEFT JOIN Statuses st ON s.status_id = st.id
                LEFT JOIN Intakes i ON s.intake_id = i.id
                LEFT JOIN Projects p ON s.project_id = p.id
                LEFT JOIN internal_eval_levels lvl ON s.pre_internship_internal_eval_level_id = lvl.id
                WHERE s.intern_id = ?''', (intern_id,))
    student = cursor.fetchone()
    conn.close()
    return student

def update_student(intern_id, data):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('UPDATE Students SET github_username = ?, full_name = ?, pronouns = ?, status_id = ?, email = ?, mobile = ?, course = ?, course_major = ?, intake_id = ?, project_id = ?, start_date = ?, end_date = ?, hours_per_week = ?, cover_letter_projects = ?, pronunciation = ?, post_internship_summary_rating_internal = ? WHERE intern_id = ?',
                   (data['github_username'], data['full_name'], data['pronouns'], data['status_id'], data['email'], data['mobile'], data['course'], data['course_major'], data['intake_id'], data['project_id'], data['start_date'], data['end_date'], data['hours_per_week'], data['cover_letter_projects'],data['pronunciation'],data['post_internship_summary_rating_internal'], intern_id))
    conn.commit()
    conn.close()

@app.route('/edit_student/<int:intern_id>', methods=['GET', 'POST'])
def edit_student(intern_id):
    if request.method == 'POST':
        # Handle form submission and update the student record in the database
        print(request.form)
        
        # Convert status name to status_id
        status_name = request.form['status']
        intake_id = int(request.form['intake_id'])  
        project_name = request.form['project']
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM Statuses WHERE name = ?', (status_name,))
        status_id_result = cursor.fetchone()
        status_id = status_id_result[0] if status_id_result else None
        
        cursor.execute('SELECT id FROM Projects WHERE name = ?', (project_name,))
        project_id_result = cursor.fetchone()
        project_id = project_id_result[0] if project_id_result else None
        conn.close()
        
        data = {
            'full_name': request.form['full_name'],
            'pronouns': request.form['pronouns'],
            'status_id': status_id,
            'email': request.form['email'],
            'mobile': request.form['mobile'],
            'course': request.form['course'],
            'course_major': request.form['course_major'],
            'github_username': request.form['github_username'],
            'intake_id': intake_id, 
            'project_id': project_id,
            'start_date': request.form['start_date'],
            'end_date': request.form['end_date'],
            'hours_per_week': request.form['hours_per_week'],
            'pronunciation': request.form['pronunciation'],
            'post_internship_summary_rating_internal': request.form['post_internship_summary_rating_internal'],
            'cover_letter_projects': request.form['cover_letter_projects'],
        }

        update_student(intern_id, data)  # Update the student record in the database

        # Redirect to the student details page after updating
        # Get the referrer URL
        referrer = request.referrer
        return redirect(referrer)

    else:
        # Retrieve the student record from the database based on the intern_id
        # Pass the student record, statuses, intakes, and projects to the edit.html template
        student = get_student_by_id(intern_id)
        statuses = get_statuses()  # Retrieve the list of statuses from the database
        intakes = get_intakes()    # Retrieve the list of intakes from the database
        projects = get_projects()  # Retrieve the list of projects from the database

    return render_template('edit.html', student=student, statuses=statuses, intakes=intakes, projects=projects)


@app.route('/share_students/<int:project_id>')
def share_students(project_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM Intakes WHERE status = "new"')
    intake_current_id = cursor.fetchone()[0]

    cursor.execute('SELECT * FROM Statuses')
    statuses = cursor.fetchall()

    if project_id == 0:
        status_of_students_to_filter = [3, 4, 5, 6]
        status_id_list = [row[0] for row in statuses if row[0] in status_of_students_to_filter]
        placeholders = ",".join(["?"] * len(status_id_list))

        query = f"""
            SELECT
                s.intern_id, s.full_name, s.email, s.mobile,
                i.name AS intake,
                s.course, s.course_major, s.cover_letter_projects, s.pronunciation,
                s.summary_tech_skills, s.summary_experience,
                s.pre_internship_summary_recommendation_external,
                s.pre_internship_technical_rating || ' ' ||
                s.pre_internship_learning_quickly || ' ' ||
                s.pre_internship_enthusiasm || ' ' ||
                s.pre_internship_experience || ' ' ||
                s.pre_internship_communication || ' ' ||
                s.pre_internship_adaptable AS student_details,
                s.github_username
            FROM Students s
            LEFT JOIN Intakes i ON s.intake_id = i.id
            WHERE s.intake_id = ?
              AND s.status_id IN ({placeholders})
        """

        cursor.execute(query, [intake_current_id] + status_id_list)

    else:
        status_of_students_to_filter = [8, 9, 10, 11, 12, 13]
        status_id_list = [row[0] for row in statuses if row[0] in status_of_students_to_filter]
        placeholders = ",".join(["?"] * len(status_id_list))

        query = f"""
            SELECT
                s.intern_id, s.full_name, s.email, s.mobile,
                i.name AS intake,
                s.course, s.course_major, s.cover_letter_projects, s.pronunciation,
                s.summary_tech_skills, s.summary_experience,
                s.pre_internship_summary_recommendation_external,
                s.pre_internship_technical_rating || ' ' ||
                s.pre_internship_learning_quickly || ' ' ||
                s.pre_internship_enthusiasm || ' ' ||
                s.pre_internship_experience || ' ' ||
                s.pre_internship_communication || ' ' ||
                s.pre_internship_adaptable AS student_details,
                s.github_username
            FROM Students s
            LEFT JOIN Intakes i ON s.intake_id = i.id
            WHERE s.intake_id = ?
                AND s.project_id = ?
                AND s.status_id IN ({placeholders})
        """

        cursor.execute(query, [intake_current_id, project_id] + status_id_list)

    students = cursor.fetchall()
    

    # Create a temporary directory to store the files
    temp_dir = 'student_intern_data/attachments/tmp'

    try:
        os.makedirs(temp_dir)
    except Exception:
        pass

    # Create the CSV file inside the temporary directory
    csv_path = os.path.join(temp_dir, 'share_student_data.csv')
    print(csv_path)
    with open(csv_path, 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['ID', 'Full Name', 'Email', 'Phone', 'Intake', 'Faculty', 'Course', 
                            'Interested in Projects', 'Pronunciation', 'Tech Skills', 'Experience', 
                            'Summary of Student', 'Details of Student', 'github username'])

        for student in students:
            # Write the student data to the CSV file
            csv_writer.writerow(student)

    # Create the ZIP file
    zip_path = 'student_intern_data/attachments/share_student_applications_temp.zip'
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        # Add the PDF files for each student to the ZIP file
        for student in students:
            intern_id = student[0]

            # Get all PDF files starting with the intern_id
            matching_files = [filename for filename in os.listdir('student_intern_data/attachments') 
                            if filename.startswith(str(intern_id)) and filename.lower().endswith('.pdf')]

            # Copy the matching PDF files to the temporary directory
            for file in matching_files:
                file_path = os.path.join('student_intern_data/attachments', file)
                dest_path = os.path.join(temp_dir, file)
                shutil.copy(file_path, dest_path)

    # Create a zip file of the other files
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        for folder_name, _, file_names in os.walk(temp_dir):
            for file_name in file_names:
                file_path = os.path.join(folder_name, file_name)
                zip_file.write(file_path, os.path.basename(file_path))

    # Remove the temporary directory
    shutil.rmtree(temp_dir)

    # Close the database connection
    conn.close()

    # Get today's date
    today = datetime.now()

    # Format the date as YYYY-mm-dd
    formatted_date = today.strftime("%Y-%m-%d")

    # Serve the ZIP file for download
    if project_id == 0:
        return send_file(zip_path, as_attachment=True, 
                        download_name=formatted_date + '_student_applications.zip')
    else:
        return send_file(zip_path, as_attachment=True, 
                        download_name=formatted_date + '_student_applications_' + project + '.zip')

@app.route('/download_contracts_and_applications')
def download_contracts_and_applications():
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # FIXED: Get the status_id for '09 Signed contract'
    cursor.execute('SELECT id FROM Statuses WHERE name = ?', ('09 Signed contract',))
    signed_contract_status_id = cursor.fetchone()[0]
    
    # FIXED: Query using status_id instead of status name
    cursor.execute('SELECT intern_id, full_name FROM Students WHERE status_id = ?', (signed_contract_status_id,))
    students = cursor.fetchall()


    # Create a temporary directory to store the files
    temp_dir = 'student_intern_data/attachments/tmp'

    try:
        os.makedirs(temp_dir)
    except Exception:
        pass

    # Create the CSV file inside the temporary directory
    csv_path = os.path.join(temp_dir, 'student_data.csv')
    with open(csv_path, 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Full Name', 'Phone', 'Email', 'Faculty', 'Start Date', 'End Date', 'Hours per Week'])

        for student in students:
            # Retrieve student data from the database
            cursor.execute('SELECT full_name, mobile, email, course, start_date, end_date, hours_per_week FROM Students WHERE intern_id = ?', (student[0],))
            student_data = cursor.fetchone()

            # Write the student data to the CSV file
            csv_writer.writerow(student_data)

    # Create the ZIP file
    zip_path = 'student_intern_data/attachments/contract_downloads_temp.zip'
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        # Add the PDF files for each student to the ZIP file
        for student in students:

            intern_id = student[0]

            # Get all PDF files starting with the intern_id
            matching_files = [filename for filename in os.listdir('student_intern_data/attachments') if filename.startswith(str(intern_id)) and filename.lower().endswith('.pdf')]

            # Copy the matching PDF files to the temporary directory
            for file in matching_files:
                file_path = os.path.join('student_intern_data/attachments', file)
                dest_path = os.path.join(temp_dir, file)
                shutil.copy(file_path, dest_path)


    # Create a zip file of the other files
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        for folder_name, _, file_names in os.walk(temp_dir):
            for file_name in file_names:
                file_path = os.path.join(folder_name, file_name)
                zip_file.write(file_path, os.path.basename(file_path))

    # Remove the temporary directory
    shutil.rmtree(temp_dir)

    # Close the database connection
    conn.close()


    # Get today's date
    today = datetime.now()

    # Format the date as YYYY-mm-dd
    formatted_date = today.strftime("%Y-%m-%d")

    # Serve the ZIP file for download
    return send_file(zip_path, as_attachment=True, download_name=formatted_date+'_contract_files.zip')


@app.route('/import_redcap', methods=['GET', 'POST'])
def import_redcap():

    today = datetime.now()

    import_dir = 'student_intern_data/import/archive'
    if request.method == 'POST':
        print(request.files)
        csv_file = request.files['csv_file']
        if csv_file:
            filename = csv_file.filename
            csv_file_path = os.path.join(import_dir, filename)
            csv_file.save(csv_file_path)

        zip_file = request.files['zip_file']
        if zip_file:
            filename = zip_file.filename
            zip_file_path = os.path.join(import_dir, filename)
            zip_file.save(zip_file_path)


        import_csv_from_redcap.read_csv_file(csv_file_path,zip_file_path)

        # Get the referrer URL
        referrer = request.referrer

        # Redirect back to the previous page
        return redirect(referrer)

    return render_template('import_redcap.html')


@app.route('/upload_application/<int:intern_id>/<string:full_name>', methods=['GET', 'POST'])
def upload_application(intern_id, full_name):

    attachments_dir = 'student_intern_data/attachments'
    if request.method == 'POST':
        file = request.files['file']
        if file:
            # Save the file to the attachments directory with the desired filename
            filename = str(intern_id)+"_"+full_name.replace(" ", "_").title()+"_application.pdf"

            file.save(os.path.join(attachments_dir, filename))
            # Get the referrer URL
            referrer = request.referrer

            # Redirect back to the previous page
            return redirect(referrer)


    return render_template('upload_application.html', intern_id=intern_id, full_name=full_name)



@app.route('/upload_signed_contract/<int:intern_id>/<string:full_name>', methods=['GET', 'POST'])
def upload_signed_contract(intern_id, full_name):

    attachments_dir = 'student_intern_data/attachments'
    if request.method == 'POST':
        file = request.files['file']
        if file:
            # Save the file to the attachments directory with the desired filename
            filename = str(intern_id)+"_"+full_name.replace(" ", "_").title()+"_signed_contract.pdf"

            file.save(os.path.join(attachments_dir, filename))
            # Get the referrer URL
            referrer = request.referrer

            # Redirect back to the previous page
            return redirect(referrer)


    return render_template('upload_signed_contract.html', intern_id=intern_id, full_name=full_name)



@app.route('/new_intake_unavailable')
def index_new_intake_unavailable():
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Projects')
    projects = cursor.fetchall()

    cursor.execute('SELECT id FROM Intakes where status = "new"')
    intake_current = cursor.fetchall()[0][0]

    # Retrieve student data from the database
    cursor.execute('SELECT * FROM Statuses')
    statuses = cursor.fetchall()

    status_of_students_to_filter = [15, 16, 17, 18, 19, 20, 21]
    status_id_list= [row[0] for row in statuses if row[0] in status_of_students_to_filter]

    # Retrieve student data from the database
    # Prepare the SQL query with a placeholder for the statuses filter
    query = '''
        SELECT s.intern_id, s.full_name, s.email, s.pronunciation, p.name, i.name AS intake, 
        s.course, st.name AS status, s.post_internship_summary_rating_internal, s.wehi_email, s.mobile
        FROM Students s
        LEFT JOIN Intakes i ON s.intake_id = i.id
        LEFT JOIN Statuses st ON s.status_id = st.id
        LEFT JOIN Projects p on s.project_id = p.id
        WHERE s.intake_id = ? AND s.status_id IN ({})
    '''.format(','.join(['?'] * len(status_id_list)))

    # Execute the query with the statuses list
    cursor.execute(query, [intake_current] + status_id_list)
    students = cursor.fetchall()
    
    # Close the database connection
    conn.close()
    
    title_of_page = "New Intake Unavailable"
    return render_template('index.html', students=students, statuses=statuses, 
                         title_of_page=title_of_page, projects=projects)

@app.route('/new_intake')
def index_new_intake():

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Projects')
    projects = cursor.fetchall()

    cursor.execute('SELECT id FROM Intakes WHERE status = "new"')
    intake_current_id = cursor.fetchall()[0][0]

    cursor.execute('SELECT * FROM Statuses')
    statuses = cursor.fetchall()
    # Retrieve student data from the database
    status_of_students_to_filter = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
    status_id_list = [row[0] for row in statuses if row[0] in status_of_students_to_filter]

    # FIXED: Added Statuses JOIN and changed s.status to st.name
    query = '''
        SELECT s.intern_id, s.full_name, s.email, s.pronunciation, p.name, i.name AS intake, 
        s.course, st.name AS status, s.post_internship_summary_rating_internal, s.pronouns,
        CAST(COALESCE(s.pre_internship_internal_eval_level_id, '') AS TEXT) || ' ' || COALESCE(lvl.name, ''),
        s.show_key_skill, s.mobile
        FROM Students s
        LEFT JOIN Intakes i ON s.intake_id = i.id
        LEFT JOIN Statuses st ON s.status_id = st.id
        LEFT JOIN Projects p ON s.project_id = p.id
        LEFT JOIN internal_eval_levels lvl ON s.pre_internship_internal_eval_level_id = lvl.id
        WHERE s.intake_id = ? AND s.status_id IN ({})
    '''.format(','.join(['?'] * len(status_id_list)))

    cursor.execute(query, [intake_current_id] + status_id_list)
    students = cursor.fetchall()

    conn.close()
    
    title_of_page = "New Intake All"
    return render_template('index.html', students=students, statuses=statuses, 
                         title_of_page=title_of_page, projects=projects)

@app.route('/outstanding')
def index_outstanding():
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Projects')
    projects = cursor.fetchall()

    cursor.execute('SELECT id FROM Intakes where status = "new"')
    intake_current = cursor.fetchall()[0][0]

    # Retrieve student data from the database
    cursor.execute('SELECT * FROM Statuses')
    statuses = cursor.fetchall()

    status_of_students_to_filter = [1, 2, 3, 4, 5, 6]
    status_id_list = [row[0] for row in statuses if row[0] in status_of_students_to_filter]

    # Retrieve student data from the database
    # Prepare the SQL query with a placeholder for the statuses filter
    query = '''
        SELECT s.intern_id, s.full_name, s.email, s.pronunciation, p.name, i.name AS intake, 
        s.course, st.name AS status, s.post_internship_summary_rating_internal, s.pronouns,
        CAST(COALESCE(s.pre_internship_internal_eval_level_id, '') AS TEXT) || ' ' || COALESCE(lvl.name, ''),
        s.show_key_skill, s.mobile
        FROM Students s
        LEFT JOIN Projects p ON s.project_id = p.id
        LEFT JOIN Intakes i ON s.intake_id = i.id
        LEFT JOIN Statuses st ON s.status_id = st.id
        LEFT JOIN internal_eval_levels lvl ON s.pre_internship_internal_eval_level_id = lvl.id
        WHERE s.intake_id = ? AND s.status_id IN ({}) ORDER BY st.name ASC
    '''.format(','.join(['?'] * len(status_id_list)))

    # Execute the query with the statuses list
    cursor.execute(query, [intake_current] + status_id_list)
    students = cursor.fetchall()

    # Close the database connection
    conn.close()
    
    title_of_page = "New Intake WIP"
    return render_template('index.html', students=students, statuses=statuses, 
                         title_of_page=title_of_page, projects=projects)


@app.route('/current')
def index_current():
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Retrieve student data from the database
    cursor.execute('SELECT * FROM Statuses')
    statuses = cursor.fetchall()

    cursor.execute('SELECT * FROM Projects')
    projects = cursor.fetchall()

    cursor.execute('SELECT id FROM Intakes where status = "current"')
    intake_current = cursor.fetchall()[0][0]

    status_of_students_current = [10, 11, 12, 13]
    status_id_list = [row[0] for row in statuses if row[0] in status_of_students_current]
    
    query = '''
        SELECT s.intern_id, s.full_name, s.email, s.pronunciation, p.name, i.name AS intake, 
        s.course, st.name AS status, s.post_internship_summary_rating_internal, s.pronouns,
        CAST(COALESCE(s.pre_internship_internal_eval_level_id, '') AS TEXT) || ' ' || COALESCE(lvl.name, ''),
        s.show_key_skill, s.mobile, s.github_username
        FROM Students s
        LEFT JOIN Projects p ON s.project_id = p.id
        LEFT JOIN Intakes i ON s.intake_id = i.id
        LEFT JOIN Statuses st ON s.status_id = st.id
        LEFT JOIN internal_eval_levels lvl ON s.pre_internship_internal_eval_level_id = lvl.id
        WHERE s.intake_id = ? AND s.status_id IN ({})
    '''.format(','.join(['?'] * len(status_id_list)))

    # Execute the query with the statuses list
    cursor.execute(query, [intake_current] + status_id_list)
    students = cursor.fetchall()

    # Close the database connection
    conn.close()
    
    title_of_page = "Currently Signed Students"
    return render_template('index.html', students=students, statuses=statuses, 
                         title_of_page=title_of_page, projects=projects)


@app.route('/')
def index():
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Retrieve student data from the database
    cursor.execute("""
        SELECT
            s.intern_id,
            s.full_name,
            s.email,
            s.pronunciation,
            p.name AS project,
            i.name AS intake,
            s.course,
            st.name AS status,
            s.post_internship_summary_rating_internal,
            s.pronouns,
            CAST(COALESCE(s.pre_internship_internal_eval_level_id, '') AS TEXT) || ' ' || COALESCE(lvl.name, ''),
            s.show_key_skill,
            s.mobile
        FROM Students s
        LEFT JOIN Projects p ON s.project_id = p.id
        LEFT JOIN Intakes i  ON s.intake_id  = i.id
        LEFT JOIN Statuses st ON s.status_id = st.id
        LEFT JOIN internal_eval_levels lvl ON s.pre_internship_internal_eval_level_id = lvl.id
    """)
    students = cursor.fetchall()



    cursor.execute('SELECT * FROM Projects')
    projects = cursor.fetchall()

    # Retrieve student data from the database
    cursor.execute('SELECT * FROM Statuses')
    statuses = cursor.fetchall()

    # Close the database connection
    conn.close()
    title_of_page = "All Students"
    return render_template('index.html', students=students,statuses=statuses,title_of_page=title_of_page,projects=projects)

@app.route('/favicon.ico')
def favicon():
    return '', 204  # Return empty response with "No Content" status

# Route to serve the file from a different directory
@app.route('/view_docs/<path:filename>')
def view_docs(filename):
    directory = 'student_intern_data/attachments/'  # Replace with the actual directory path
    filepath = directory + '/' + filename
    return send_file(filepath, as_attachment=False)

@app.route('/view/<int:intern_id>')
def student(intern_id):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Retrieve student data from the database
    # query everything
    cursor.execute('''SELECT s.intern_id, s.full_name, s.pronouns, st.name, s.email, s.mobile, s.course, s.course_major, 
                s.link_to_application_doc, s.read_student_handbook, s.read_student_projects, s.cover_letter_projects, 
                s.cover_letter_concept, s.cover_letter_technical, s.pronunciation, p.name, s.start_date, s.end_date, 
                s.hours_per_week, i.name, s.supervisor_email, s.wehi_email, s.summary_tech_skills, s.summary_experience, 
                s.summary_interest_in_projects, s.pre_internship_summary_recommendation_external, 
                CAST(COALESCE(s.pre_internship_internal_eval_level_id, '') AS TEXT) || ' ' || COALESCE(lvl.name, ''), 
                s.pre_internship_technical_rating, s.pre_internship_social_rating, s.pre_internship_learning_quickly, 
                s.pre_internship_enthusiasm, s.pre_internship_experience, s.pre_internship_communication, 
                s.pre_internship_adaptable, s.pre_internship_problem_solver, s.post_internship_comments, 
                s.post_internship_adaptability, s.post_internship_learn_technical, s.post_internship_learn_conceptual, 
                s.post_internship_collaborative, s.post_internship_ambiguity, s.post_internship_complexity, 
                s.post_internship_summary_rating_internal, s.post_internship_summary_rating_external, s.github_username, 
                s.extra_notes, s.remote_internship, s.code_of_conduct, s.facilitator_follower, s.listener_or_talker, 
                s.thinker_brainstormer, s.why_applied, s.projects_recommended, s.redcap_id, s.show_key_skill 
                FROM Students s 
                LEFT JOIN Statuses st ON s.status_id = st.id
                LEFT JOIN Intakes i ON s.intake_id = i.id
                LEFT JOIN Projects p ON s.project_id = p.id
                LEFT JOIN internal_eval_levels lvl ON s.pre_internship_internal_eval_level_id = lvl.id
                WHERE s.intern_id = ?''', (intern_id,))
    student = cursor.fetchone()

    # Close the database connection
    conn.close()

    # Find matching PDF files
    attachments_dir = 'student_intern_data/attachments'
    matching_files = []
    for filename in os.listdir(attachments_dir):
        if filename.startswith(str(intern_id)) and filename.lower().endswith('.pdf'):
            matching_files.append(filename)

    # Pass matching_files to the template
    return render_template('view.html', student=student, matching_files=matching_files)


@app.route('/change_phone', methods=['POST'])
def change_phone():
    data = request.get_json()
    student_ids = data.get('student_ids', [])
    new_phone = data.get('new_phone', '')
    # Convert student IDs to integers
    student_ids = [int(id) for id in student_ids]
    # Call the change_student_project function
    change_phone_update(student_ids, new_phone)
    # Redirect back to the index page
    return redirect('/')

@app.route('/change_pronouns', methods=['POST'])
def change_pronouns():
    data = request.get_json()
    student_ids = data.get('student_ids', [])
    new_pronouns = data.get('new_pronouns', '')
    # Convert student IDs to integers
    student_ids = [int(id) for id in student_ids]
    # Call the change_student_project function
    change_pronouns_update(student_ids, new_pronouns)
    # Redirect back to the index page
    return redirect('/')

@app.route('/change_course', methods=['POST'])
def change_course():
    data = request.get_json()
    student_ids = data.get('student_ids', [])
    new_course = data.get('new_course', '')
    # Convert student IDs to integers
    student_ids = [int(id) for id in student_ids]
    # Call the change_student_project function
    change_course_update(student_ids, new_course)
    # Redirect back to the index page
    return redirect('/')


@app.route('/change_post_internship_rating', methods=['POST'])
def change_post_internship_rating():

    data = request.get_json()
    student_ids = data.get('student_ids', [])
    new_project = data.get('new_post_internship_rating', '')

    # Convert student IDs to integers
    student_ids = [int(id) for id in student_ids]

    # Call the change_student_project function
    change_post_internship_rating(student_ids, new_project)

    # Redirect back to the index page
    return redirect('/')



@app.route('/change_project', methods=['POST'])
def change_project():

    data = request.get_json() or {}
    student_ids = data.get('student_ids', [])
    new_project_id = data.get('new_project_id')

    if new_project_id is None:
        return ("Missing project_id", 400)

    # Convert IDs to integers
    student_ids = [int(sid) for sid in student_ids]
    new_project_id = int(new_project_id)

    # Call the change_student_project function
    change_student_project(student_ids, new_project_id)

    # Redirect back to the index page
    return redirect('/')


@app.route('/change_status', methods=['POST'])
def change_status():

    data = request.get_json()
    student_ids = data.get('student_ids', [])
    new_status_id = data.get('new_status_id', '')

    # Convert student IDs and status_id to integers
    student_ids = [int(id) for id in student_ids]
    new_status_id = int(new_status_id)

    # Call the change_student_status function
    change_student_status(student_ids, new_status_id)

    # Redirect back to the index page
    return redirect('/')

def change_student_status(student_ids, new_status_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Prepare the SQL query
    query = '''
        UPDATE Students
        SET status_id = ?
        WHERE intern_id IN ({})
    '''.format(','.join(['?'] * len(student_ids)))

    # Execute the query
    cursor.execute(query, [new_status_id] + student_ids)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


def change_post_internship_rating(student_ids, new_post_internship_rating):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Prepare the SQL query
    query = '''
        UPDATE Students
        SET post_internship_summary_rating_internal = ?
        WHERE intern_id IN ({})
    '''.format(','.join(['?'] * len(student_ids)))

    # Execute the query
    cursor.execute(query, [new_post_internship_rating] + student_ids)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def change_phone_update(student_ids, new_phone):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Prepare the SQL query
    query = '''
        UPDATE Students
        SET mobile = ?
        WHERE intern_id IN ({})
    '''.format(','.join(['?'] * len(student_ids)))

    # Execute the query
    cursor.execute(query, [new_phone] + student_ids)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


def change_pronouns_update(student_ids, new_pronouns):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Prepare the SQL query
    query = '''
        UPDATE Students
        SET pronouns = ?
        WHERE intern_id IN ({})
    '''.format(','.join(['?'] * len(student_ids)))

    # Execute the query
    cursor.execute(query, [new_pronouns] + student_ids)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


def change_course_update(student_ids, new_course):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Prepare the SQL query
    query = '''
        UPDATE Students
        SET course = ?
        WHERE intern_id IN ({})
    '''.format(','.join(['?'] * len(student_ids)))

    # Execute the query
    cursor.execute(query, [new_course] + student_ids)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


def change_student_project(student_ids, project_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Prepare the SQL query
    query = '''
        UPDATE Students
        SET project_id = ?
        WHERE intern_id IN ({})
    '''.format(','.join(['?'] * len(student_ids)))

    # Execute the query
    cursor.execute(query, [project_id] + student_ids)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


def calculate_breakdown_of_students(students):
    # rating in index 5
    ratings = [student[5] for student in students]

    breakdown_ratings = dict(Counter(ratings))
    total_students = len(students)

    # course in index 4
    courses = [student[4] for student in students]
    breakdown_courses = dict(Counter(courses))

    # status in index 3
    statuses = [student[3] for student in students]
    breakdown_statuses = dict(Counter(statuses))

    return [
        breakdown_ratings,
        breakdown_courses,
        total_students,
        breakdown_statuses
    ]


#pronouns breakdown
def calculate_breakdown_of_pronouns(students):
    pronoun_data = {}
    total_students = len(students)

    # Count the occurrences of each pronoun and track associated statuses
    for student in students:
        pronouns = student[2]  # Assuming pronouns column is at index 2
        status = student[3]  # Assuming status column is at index 3

        if pronouns in pronoun_data:
            pronoun_data[pronouns]['count'] += 1
            pronoun_data[pronouns]['statuses'].add(status)
        else:
            pronoun_data[pronouns] = {
                'count': 1,
                'statuses': {status}
            }

    # Calculate the percentage for each pronoun
    pronoun_percentage = {}
    for pronouns, data in pronoun_data.items():
        percentage = (data['count'] / total_students) * 100
        pronoun_percentage[pronouns] = round(percentage, 2)
        data['statuses'] = ', '.join(data['statuses'])  # Convert set of statuses to comma-separated string

    return pronoun_data, pronoun_percentage, total_students


@app.route('/dashboard/<string:dashboard_type>',methods=['GET'])
def dashboard(dashboard_type):
    try:
        print(dashboard_type)
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Retrieve student data from the database
        cursor.execute('SELECT * FROM Statuses')
        statuses = cursor.fetchall()
        if dashboard_type == "new_all":
            status_of_students_current_and_past = [1,2,3,4,5,6,7,8,9,10,11,12]
        if dashboard_type == "finished":
            status_of_students_current_and_past = [14]
        if dashboard_type == "current":
            status_of_students_current_and_past = [13]
        if dashboard_type == "new_signed_and_offered":
            status_of_students_current_and_past = [7,8,9,10,11,12]
        if dashboard_type == "new_signed_and_accepted":
            status_of_students_current_and_past = [8,9,10,11,12]
        if dashboard_type == "new_signed":
            status_of_students_current_and_past = [9,10,11,12]
        if dashboard_type == "all":
            status_of_students_current_and_past = [8,9, 10, 11, 12, 13, 14]
        # FIXED: Get status IDs instead of names
        status_id_list = [row[0] for row in statuses if row[0] in status_of_students_current_and_past]

        # Retrieve student data from the database
        # Prepare the SQL query with placeholders for the statuses filter and pronouns
        query = '''
            SELECT s.intern_id, s.full_name, s.pronouns, st.name AS status, s.course, 
                s.post_internship_summary_rating_internal, s.intake_id
            FROM Students s
            LEFT JOIN Statuses st ON s.status_id = st.id
            WHERE s.status_id IN ({}) AND s.pronouns IS NOT NULL
        '''.format(','.join(['?'] * len(status_id_list)))


        # Execute the query with the statuses list
        cursor.execute(query, status_id_list)

        # Retrieve student data from the database
        students = cursor.fetchall()
        total_students_current_and_past = len(students)

        # Close the database connection
        conn.close()

        result = calculate_breakdown_of_students(students)

        breakdown_ratings = result[0]
        breakdown_courses = result[1]
        total_students = result[2]
        breakdown_statuses = result[3]

        pronoun_data, pronoun_percentage, total_students = calculate_breakdown_of_pronouns(students)

        return render_template('dashboard.html', students=students, breakdown_ratings=breakdown_ratings,
                            breakdown_courses=breakdown_courses,
                            total_students=total_students, pronoun_data=pronoun_data,
                            pronoun_percentage=pronoun_percentage,breakdown_statuses=breakdown_statuses,total_students_current_and_past = total_students_current_and_past,
                            dashboard_type = dashboard_type)
    except Exception:
        traceback.print_exc()   
        raise

    @app.route('/dashboard/<string:dashboard_type>/chart_data', methods=['GET'])
    def dashboard_chart_data(dashboard_type):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # FIXED: First get the status_id for '14 Finished'
        cursor.execute("SELECT id FROM Statuses WHERE name = '14 Finished'")
        finished_status_id = cursor.fetchone()[0]

        # Retrieve students by intake and calculate hours per week
        cursor.execute('''
            SELECT intakes.name AS intake_name,
                SUM(CASE 
                        WHEN Students.course = 'Engineering and IT' THEN 300
                        WHEN Students.course = 'Engineering' THEN 300
                        WHEN Students.course = 'Science Full Year' THEN 200
                        WHEN Students.course = 'Science' THEN 100
                        WHEN Students.course = 'Volunter' THEN 100
                        ELSE 100
                    END) AS total_hours,
                COUNT(*) AS student_count
            FROM Students
            JOIN Intakes ON Students.intake_id = Intakes.id
            WHERE Students.status_id = ? AND Intakes.status = 'finished'
            GROUP BY Students.intake_id, intakes.name
            ORDER BY Intakes.id ASC
        ''', (finished_status_id,))
        
        data = cursor.fetchall()
        conn.close()

        # Format the response
        chart_data = {
            "intakes": [row[0] for row in data], 
            "total_hours": [row[1] for row in data],
            "student_count": [row[2] for row in data]
        }

        return jsonify(chart_data)
    



@app.route('/intakes')
def intakes_index():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Retrieve all intakes
    cursor.execute('SELECT * FROM Intakes')
    intakes = cursor.fetchall()

    query = """
        SELECT
            s.intern_id,
            s.full_name,
            s.email,
            s.pronunciation,
            p.name AS project,
            i.name AS intake,
            s.course,
            st.name AS status
        FROM Students s
        LEFT JOIN Projects p ON s.project_id = p.id
        LEFT JOIN Intakes  i ON s.intake_id  = i.id
        LEFT JOIN Statuses st ON s.status_id = st.id
    """
    cursor.execute(query)
    students = cursor.fetchall()

    conn.close()
    return render_template('intakes.html', intakes=intakes, students=students)


@app.route('/statuses')
def statuses_index():
    # Connect to database and retrieve all status records
    # Note: Status IDs are referenced throughout the application:
    #   - IDs 10-13: "Current" students (quick review to interviewed)
    #   - IDs 1-6: Early-stage applicants
    #   - IDs 15-21: Finished/unavailable students
    # Changing IDs will break hardcoded filters in multiple routes
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, name FROM Statuses ORDER BY id')
    statuses = cursor.fetchall()
    
    conn.close()
    return render_template('statuses_index.html', statuses=statuses)


@app.route('/add_status', methods=['GET', 'POST'])
def add_status():
    if request.method == 'POST':
        new_name = request.form.get('name')

        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Insert the new status record into the database
        cursor.execute('INSERT INTO Statuses (name) VALUES (?)', (new_name,))
        
        conn.commit()
        conn.close()

        return redirect(url_for('statuses_index'))

    # If it's a GET request, render the add_status.html template
    return render_template('add_status.html')


@app.route('/edit_status/<int:status_id>', methods=['GET', 'POST'])
def edit_status(status_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if request.method == 'POST':
        # Handle form submission and update the status record
        new_name = request.form.get('name')
        cursor.execute('UPDATE Statuses SET name = ? WHERE id = ?', (new_name, status_id))
        conn.commit()
        conn.close()
        # Redirect to statuses index after saving changes
        return redirect(url_for('statuses_index'))

    # If it's a GET request, render the edit_status.html template
    cursor.execute('SELECT * FROM Statuses WHERE id = ?', (status_id,))
    status_data = cursor.fetchone()
    conn.close()

    return render_template('edit_status.html', status=status_data)


@app.route('/students_by_intake/<path:intake_name>')  # Use <path:> to allow slashes in the parameter
def students_by_intake(intake_name):
    intake_name = unquote(intake_name)  # Decode the intake name
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()

    # Resolve intake_name to intake_id
    cursor.execute('SELECT id FROM Intakes WHERE name = ?', (intake_name,))
    res = cursor.fetchone()
    intake_id = res[0] if res else None

    query = """
        SELECT
            s.intern_id,
            s.full_name,
            s.email,
            s.pronunciation,
            p.name AS project,
            i.name AS intake,
            s.course,
            st.name AS status,
            s.post_internship_summary_rating_internal,
            s.pronouns,
            CAST(COALESCE(s.pre_internship_internal_eval_level_id, '') AS TEXT) || ' ' || COALESCE(lvl.name, ''),
            s.show_key_skill,
            s.mobile,
            s.github_username
        FROM Students s
        LEFT JOIN Projects p ON s.project_id = p.id
        LEFT JOIN Intakes i  ON s.intake_id  = i.id
        LEFT JOIN Statuses st ON s.status_id = st.id
        LEFT JOIN internal_eval_levels lvl ON s.pre_internship_internal_eval_level_id = lvl.id
        WHERE s.intake_id = ?
    """
    cursor.execute(query, (intake_id,))
    students = cursor.fetchall()



    # Retrieve student data from the database
    cursor.execute('SELECT * FROM Statuses')
    statuses = cursor.fetchall()

    cursor.execute('SELECT * FROM Projects')
    projects = cursor.fetchall()

    conn.close()

    title_of_page = f"Students in Intake: {intake_name}"
    return render_template('index.html', students=students, statuses=statuses, projects=projects, intake_name=intake_name, title_of_page=title_of_page)


@app.route('/finished_students_by_intake/<path:intake_name>')
def finished_students_by_intake(intake_name):
    intake_name = unquote(intake_name)
    import os

    db_path = 'student_intern_data/student_intern_data.db'
    print("CWD =", os.getcwd())
    print("DB ABS =", os.path.abspath(db_path))

    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()

    # Resolve intake_name to intake_id
    cursor.execute('SELECT id FROM Intakes WHERE name = ?', (intake_name,))
    res = cursor.fetchone()
    intake_id = res[0] if res else None

    # FIXED: Get status_id for '14 Finished'
    cursor.execute("SELECT id FROM Statuses WHERE name = '14 Finished'")
    finished_status_id = cursor.fetchone()[0]

    # FIXED: Added JOIN with Statuses and using status_id
    query = '''
        SELECT s.intern_id, s.full_name, s.email, s.pronunciation, p.name, 
                i.name AS intake, s.course, st.name AS status, 
                s.post_internship_summary_rating_internal, s.pronouns,
                CAST(COALESCE(s.pre_internship_internal_eval_level_id, '') AS TEXT) || ' ' || COALESCE(lvl.name, ''),
                s.show_key_skill, s.mobile, s.github_username
        FROM Students s
        LEFT JOIN Intakes i ON s.intake_id = i.id
        LEFT JOIN Statuses st ON s.status_id = st.id
        LEFT JOIN Projects p ON s.project_id = p.id
        LEFT JOIN internal_eval_levels lvl ON s.pre_internship_internal_eval_level_id = lvl.id
        WHERE s.intake_id = ? AND s.status_id = ?
    '''
    cursor.execute(query, (intake_id, finished_status_id))
    students = cursor.fetchall()

    # Retrieve student data from the database
    cursor.execute('SELECT * FROM Statuses')
    statuses = cursor.fetchall()

    cursor.execute('SELECT * FROM Projects')
    projects = cursor.fetchall()

    conn.close()

    title_of_page = f"Finished Students in Intake: {intake_name}"
    return render_template('index.html', students=students, intake_name=intake_name, 
                         statuses=statuses, projects=projects, title_of_page=title_of_page)


@app.route('/edit_intake/<int:intake_id>', methods=['GET', 'POST'])
def edit_intake(intake_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    if request.method == 'POST':
        # Handle form submission and update the intake record in your database
        new_name = request.form.get('name')
        new_status = request.form.get('status')
        new_start_date = request.form.get('intake_start_date')
        cursor = conn.cursor()
        cursor.execute('UPDATE Intakes SET name = ?, status = ?, intake_start_date = ? WHERE id = ?', (new_name, new_status, new_start_date, intake_id))
        conn.commit()
        conn.close()
        # Redirect to previous page after saving changes
        return redirect(url_for('intakes_index'))



    # If it's a GET request, render the edit_intake.html template
    cursor.execute('SELECT * FROM Intakes where id = ?', (intake_id,))
    intake_data = cursor.fetchone()
    conn.close()


    return render_template('edit_intake.html', intake=intake_data)

@app.route('/add_intake', methods=['GET', 'POST'])
def add_intake():
    if request.method == 'POST':
        new_name = request.form.get('name')
        new_status = request.form.get('status')
        intake_date = request.form.get('intake_start_date')

        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Insert the new intake record into the database using intake_start_date
        cursor.execute('INSERT INTO Intakes (name, status, intake_start_date) VALUES (?, ?, ?)', 
                      (new_name, new_status, intake_date))
        
        # Get the newly created intake ID
        intake_id = cursor.lastrowid
        
        # Create default email schedule for this intake
        cursor.execute('''INSERT INTO EmailSchedule (intake_id, week_number, week_offset_days, subject, body) VALUES 
                         (?, '0 - 1 week before', -7, '1 week before WEHI internship', 'Hi All, This is your email to start your internship preparation...'),
                         (?, '1 - First week', 0, 'First week of WEHI internship', 'Hi All, Welcome to your first week of internship...'),
                         (?, '2 - Second week', 7, 'Second week of WEHI internship', 'Hi All, This is your second week of internship...'),
                         (?, '4 - Fourth week', 21, 'Fourth week of WEHI internship', 'Hi All, This is your email to start week 4 of your internship...'),
                         (?, '10 - Tenth week', 63, 'Tenth week of WEHI internship', 'Hi All, This is your email to start week 10 of your internship...'),
                         (?, '13 - End of internship', 84, 'End of WEHI internship', 'Hi All, I would like to thank you all for being a part of this intake...')''',
                      (intake_id, intake_id, intake_id, intake_id, intake_id, intake_id))
        
        conn.commit()

        # Close the database connection
        conn.close()

        return redirect(url_for('intakes_index'))

    # If it's a GET request, render the add_intake.html template
    return render_template('add_intake.html')


@app.route('/add_weekly_email/<int:intake_id>', methods=['GET', 'POST'])
def add_weekly_email(intake_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get intake information
    cursor.execute('SELECT id, name, intake_start_date FROM Intakes WHERE id = ?', (intake_id,))
    intake = cursor.fetchone()
    
    if not intake:
        return redirect(url_for('intakes_index'))
    
    if request.method == 'POST':
        week_number = request.form.get('week_number')
        week_description = request.form.get('week_description')
        subject = request.form.get('subject')
        body = request.form.get('body')
        
        # Calculate week_offset_days based on week number
        # Week 0 = -7 days (1 week before), Week 1 = 0 days (start week), Week 2 = 7 days, etc.
        week_offset_days = (int(week_number) - 1) * 7
        
        # Create formatted week number string
        week_number_formatted = f"{week_number} - {week_description}"
        
        # Insert the new weekly email into the database
        cursor.execute('''INSERT INTO EmailSchedule (intake_id, week_number, week_offset_days, subject, body, last_modified) 
                         VALUES (?, ?, ?, ?, ?, CURRENT_DATE)''', 
                      (intake_id, week_number_formatted, week_offset_days, subject, body))
        
        conn.commit()
        conn.close()
        
        return redirect(url_for('email_intake', intake_id=intake_id))
    
    # GET request - show the form
    conn.close()
    return render_template('add_weekly_email.html', intake_id=intake_id, intake_name=intake[1])


@app.route('/projects')
def projects_index():
    projects = get_all_projects()
    return render_template('projects.html', projects=projects)

@app.route('/project_students/<int:id>')
def project_students(id):
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()

    # Get project name
    cursor.execute('SELECT name FROM Projects WHERE id = ?', (id,))
    name = cursor.fetchone()
    name = name[0] if name else "Unknown Project"

    # Get students associated with this project
    query = """
        SELECT
            s.intern_id,
            s.full_name,
            s.email,
            s.pronunciation,
            p.name AS project,
            i.name AS intake,
            s.course,
            st.name AS status,
            s.post_internship_summary_rating_internal,
            s.pronouns,
            CAST(COALESCE(s.pre_internship_internal_eval_level_id, '') AS TEXT) || ' ' || COALESCE(lvl.name, ''),
            s.show_key_skill,
            s.mobile
        FROM Students s
        LEFT JOIN Projects p ON s.project_id = p.id
        LEFT JOIN Intakes i  ON s.intake_id  = i.id
        LEFT JOIN Statuses st ON s.status_id = st.id
        LEFT JOIN internal_eval_levels lvl ON s.pre_internship_internal_eval_level_id = lvl.id
        WHERE s.project_id = ?
    """
    cursor.execute(query, (id,))
    students = cursor.fetchall()


 # Retrieve student data from the database
    cursor.execute('SELECT * FROM Statuses')
    statuses = cursor.fetchall()

    cursor.execute('SELECT * FROM Projects')
    projects = cursor.fetchall()

    conn.close()

    title_of_page = f"Students in Project: {name}"
    return render_template('index.html', students=students, name=name, statuses=statuses, projects=projects, title_of_page=title_of_page)

@app.route('/project_finished_students/<int:id>')
def project_finished_students(id):
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()

    # Get project name
    cursor.execute('SELECT name FROM Projects WHERE id = ?', (id,))
    name = cursor.fetchone()
    name = name[0] if name else "Unknown Project"

   # FIXED: Get status_id for '14 Finished'
    cursor.execute("SELECT id FROM Statuses WHERE name = '14 Finished'")
    finished_status_id = cursor.fetchone()[0]

    # FIXED: Added JOINs and using status_id
    query = """
        SELECT
            s.intern_id,
            s.full_name,
            s.email,
            s.pronunciation,
            p.name AS project,
            i.name AS intake,
            s.course,
            st.name AS status,
            s.post_internship_summary_rating_internal,
            s.pronouns,
            CAST(COALESCE(s.pre_internship_internal_eval_level_id, '') AS TEXT) || ' ' || COALESCE(lvl.name, ''),
            s.show_key_skill,
            s.mobile
        FROM Students s
        LEFT JOIN Projects p ON s.project_id = p.id
        LEFT JOIN Intakes i  ON s.intake_id  = i.id
        LEFT JOIN Statuses st ON s.status_id = st.id
        LEFT JOIN internal_eval_levels lvl ON s.pre_internship_internal_eval_level_id = lvl.id
        WHERE s.project_id = ?
        AND s.status_id = ?
    """
    cursor.execute(query, (id, finished_status_id))
    students = cursor.fetchall()



    # Retrieve student data from the database
    cursor.execute('SELECT * FROM Statuses')
    statuses = cursor.fetchall()

    cursor.execute('SELECT * FROM Projects')
    projects = cursor.fetchall()

    conn.close()

    title_of_page = f"Students in Project: {name}"
    return render_template('index.html', students=students, name=name, statuses=statuses, projects=projects, title_of_page=title_of_page)

@app.route('/project_current_students/<int:id>')
def project_current_students(id):
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()

    # Get project name
    cursor.execute('SELECT name FROM Projects WHERE id = ?', (id,))
    name = cursor.fetchone()
    name = name[0] if name else "Unknown Project"

    # FIXED: Get status_id for '13 Internship started'
    cursor.execute("SELECT id FROM Statuses WHERE name = '13 Internship started'")
    current_status_id = cursor.fetchone()[0]

    # FIXED: Added JOINs and using status_id
    query = """
        SELECT
            s.intern_id,
            s.full_name,
            s.email,
            s.pronunciation,
            p.name AS project,
            i.name AS intake,
            s.course,
            st.name AS status,
            s.post_internship_summary_rating_internal,
            s.pronouns,
            CAST(COALESCE(s.pre_internship_internal_eval_level_id, '') AS TEXT) || ' ' || COALESCE(lvl.name, ''),
            s.show_key_skill,
            s.mobile
        FROM Students s
        LEFT JOIN Projects p  ON s.project_id = p.id
        LEFT JOIN Intakes  i  ON s.intake_id  = i.id
        LEFT JOIN Statuses st ON s.status_id  = st.id
        LEFT JOIN internal_eval_levels lvl ON s.pre_internship_internal_eval_level_id = lvl.id
        WHERE s.project_id = ?
        AND s.status_id  = ?
    """
    cursor.execute(query, (id, current_status_id))
    students = cursor.fetchall()



    # Retrieve student data from the database
    cursor.execute('SELECT * FROM Statuses')
    statuses = cursor.fetchall()

    cursor.execute('SELECT * FROM Projects')
    projects = cursor.fetchall()

    conn.close()

    title_of_page = f"Students in Project: {name}"
    return render_template('index.html', students=students, name=name, statuses=statuses, projects=projects, title_of_page=title_of_page)


@app.route('/add_project', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        new_name = request.form.get('name')
        new_status = request.form.get('status')

        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Insert the new project record into the database
        cursor.execute('INSERT INTO projects (name, status) VALUES (?, ?)', (new_name, new_status))
        conn.commit()

        # Close the database connection
        conn.close()

        return redirect(url_for('projects_index'))

    # If it's a GET request, render the add_project.html template
    return render_template('add_project.html')

@app.route('/edit_project/<int:project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if request.method == 'POST':
        # Handle form submission and update the project record in your database
        new_name = request.form.get('name')
        new_status = request.form.get('status')

        # Perform the database update logic here
        # Update the project record with the new_name and new_status
        cursor = conn.cursor()

        # Update the project record in the database
        cursor.execute('UPDATE projects SET name = ?, status = ? WHERE id = ?', (new_name, new_status, project_id))
        conn.commit()



    cursor.execute('SELECT * FROM projects where id = ?', (project_id,))
    project_data = cursor.fetchone()
    conn.close()


    return render_template('edit_project.html', project=project_data)

def create_email_intake_table_rows(intake_start_date_object):

    body_before = """Hi All, %0D%0A%0D%0AWelcome to the RCP Student Internship Program at WEHI. We are excited to have you join our team and provide you with valuable learning opportunities throughout your internship. %0D%0A%0D%0APlease read through the onboarding document https://doi.org/10.6084/m9.figshare.23280815 as this will help you ease your way into WEHI. %0D%0A%0D%0AI will be adding your student email to the WEHI system so you can gain access to our Sharepoint. This is temporary as you will be given a WEHI email address via Workday. %0D%0A%0D%0AWorkday is the Human Resources software tool at WEHI. You will receive an email from Workday and will need to fill in all the forms before you start. You may not receive the Workday email before your start date. This is OK, you will just need to wait and use your student email for the time being. Please also note that there is a Workday FAQ you can find in the FAQ below.%0D%0A%0D%0AHere are a few things you can do before you start: %0D%0A%0D%0A- You can read about the top 5 mistakes that students make https://wehi-researchcomputing.github.io/top-5-mistakes%0D%0A%0D%0A- You can also have a look at the FAQ online https://wehi-researchcomputing.github.io/faq%0D%0A%0D%0A- You can learn how to handle a complex and ambiguous project https://wehi-researchcomputing.github.io/complex-projects %0D%0A%0D%0A- You can review your project and look at the available documentation https://wehi-researchcomputing.github.io/project-wikis%0D%0A%0D%0AIf you have any questions or need further clarification regarding the internship program or the onboarding document, please feel free to reach out to me after you have looked through these documents. We are here to assist you and provide any necessary support. %0D%0A%0D%0AWe are looking forward to working with you and wish you a rewarding and successful internship experience."""

    body_first = """Hi All,%0D%0A%0D%0AThis is your email to start week 1 of your internship. You are probably excited and a little bit anxious too. That’s OK. Please remember you have other students to connect with and you can always ask your supervisor or me for help.%0D%0A%0D%0APlease read through the onboarding document https://doi.org/10.6084/m9.figshare.23280815 as this will help you ease your way into WEHI. %0D%0A%0D%0AI will be adding your student email to the WEHI system so you can gain access to our Sharepoint. This is temporary as you will be given a WEHI email address via Workday. %0D%0A%0D%0AWorkday is the Human Resources software tool at WEHI. You will find more details in the onbording document. Please also note that there is a Workday FAQ you can find in the FAQ below.%0D%0A%0D%0AHere are a few things you can do this week: %0D%0A%0D%0A- You can create your technical diary to help you track what you did to run a command or fix a mistake. This should be stored in Sharepoint under your project under its own folder. This folder should be shared in the weekly email update. %0D%0A%0D%0A- You can read about the top 5 mistakes that students make https://wehi-researchcomputing.github.io/top-5-mistakes%0D%0A%0D%0A- You can also have a look at the FAQ online https://wehi-researchcomputing.github.io/faq%0D%0A%0D%0A- You can learn how to handle a complex and ambiguous project https://wehi-researchcomputing.github.io/complex-projects %0D%0A%0D%0A- You can review your project and look at the available documentation https://wehi-researchcomputing.github.io/project-wikis%0D%0A%0D%0AIf you have any questions or need further clarification regarding the internship program or the onboarding document, please feel free to reach out to me after you have looked through these documents. We are here to assist you and provide any necessary support. %0D%0A%0D%0AWe are looking forward to working with you and wish you a rewarding and successful internship experience."""

    body_second="""Hi All,%0D%0A%0D%0AThis is your email to start week 2 of your internship. You are probably getting your head around the concepts and perhaps still feeling a little bit anxious too. That’s OK. Please remember that this is a “best-effort” internship for most of you and we are trying to see how good you really are in a safe environment. Remember, you can always ask your supervisor or me for help. %0D%0A%0D%0APlease read through the onboarding document https://doi.org/10.6084/m9.figshare.23280815 as this will help you ease your way into WEHI. %0D%0A%0D%0APlease also make sure you have a system of emailing your supervisor at least once a week for an update, and that you are documenting what you are learning in a wiki and a technical document on Sharepoint. You will be expected to answer questions about the project by the end of week 4.%0D%0A%0D%0AHere are a few things you can do if you haven’t done already: %0D%0A%0D%0A- You can create your technical diary to help you track what you did to run a command or fix a mistake. This should be stored in Sharepoint under your project under its own folder. This folder should be shared in the weekly email update.%0D%0A%0D%0A- You can read about the top 5 mistakes that students make https://wehi-researchcomputing.github.io/top-5-mistakes%0D%0A%0D%0A- You can also have a look at the FAQ online https://wehi-researchcomputing.github.io/faq%0D%0A%0D%0A- You can learn how to handle a complex and ambiguous project https://wehi-researchcomputing.github.io/complex-projects %0D%0A%0D%0A- You can review your project and look at the available documentation https://wehi-researchcomputing.github.io/project-wikis%0D%0A%0D%0AIf you have any questions or need further clarification regarding the internship program or the onboarding document, please feel free to reach out to me after you have looked through these documents. We are here to assist you and provide any necessary support. %0D%0A%0D%0AWe are looking forward to working with you and wish you a rewarding and successful internship experience."""
    body_fourth="""Hi All, %0D%0A%0D%0AThis is your email to start week 4 of your internship. Hopefully you are in the swing of things by now. If not, please let me know if I can help. %0D%0A%0D%0AThis week we will be asking you to explain what you know about the high-level nuances of the project. This is to make sure you can understand why you are doing things and to make it easier and faster for you to work later in the project.%0D%0A%0D%0AAs always: %0D%0A%0D%0A- You can create your technical diary to help you track what you did to run a command or fix a mistake. This should be stored in Sharepoint under your project under its own folder. This folder should be shared in the weekly email update.%0D%0A%0D%0A- You can refer to the onboarding document https://doi.org/10.6084/m9.figshare.23280815%0D%0A%0D%0A- You can read about the top 5 mistakes that students make https://wehi-researchcomputing.github.io/top-5-mistakes %0D%0A%0D%0A- You can also have a look at the FAQ online https://wehi-researchcomputing.github.io/faq %0D%0A%0D%0A- You can learn how to handle a complex and ambiguous project https://wehi-researchcomputing.github.io/complex-projects %0D%0A%0D%0A- You can review your project and look at the available documentation https://wehi-researchcomputing.github.io/project-wikis %0D%0A%0D%0AIf you have any questions or need further clarification regarding the internship program or the onboarding document, please feel free to reach out to me. We are here to assist you and provide any necessary support."""
    body_tenth="""Hi All, %0D%0A%0D%0AThis is your email to start week 10 of your internship. This is the time when we want you to start reflecting and wrapping up the project. This is the time we want to see what your final presentations might look like, make sure the wiki is up to date and that your technical diary is in Sharepoint. When writing your presentation, please make sure the Acknowledgement slide is appropriate – you can see this in the onboarding document.%0D%0A%0D%0AAs always: %0D%0A%0D%0A- You can create your technical diary to help you track what you did to run a command or fix a mistake. This should be stored in Sharepoint under your project under its own folder. This folder should be shared in the weekly email update.%0D%0A%0D%0A- You can refer to the onboarding document https://doi.org/10.6084/m9.figshare.23280815%0D%0A%0D%0A- You can read about the top 5 mistakes that students make https://wehi-researchcomputing.github.io/top-5-mistakes %0D%0A%0D%0A- You can also have a look at the FAQ online https://wehi-researchcomputing.github.io/faq %0D%0A%0D%0A- You can learn how to handle a complex and ambiguous project https://wehi-researchcomputing.github.io/complex-projects %0D%0A%0D%0A- You can review your project and look at the available documentation https://wehi-researchcomputing.github.io/project-wikis %0D%0A%0D%0AIf you have any questions or need further clarification regarding the internship program or the onboarding document, please feel free to reach out to me. We are here to assist you and provide any necessary support. """
    body_end="""Hi All,%0D%0A%0D%0AI would like to thank you all for being a part of this intake at WEHI, and for all your efforts. I hope that you were able to benefit from this internship.%0D%0A%0D%0ATo help us improve, please provide anonymous feedback on the student internship https://forms.office.com/r/XLTukQ9stB %0D%0A%0D%0AWe hope you will keep in touch with your teammates and supervisors. One way of doing this is to reach out via LinkedIn.%0D%0A%0D%0AAnother way to continue sharing your work from the internship. With the permission of your supervisor, consider uploading your presentation to a platform like Figshare or Zenodo. By doing so, you can make your findings and insights accessible to a wider audience.%0D%0A%0D%0AWhen sharing your work on Figshare or a similar platform, remember to acknowledge your team mates as a co-author or contributor. Including them as an author ensures that credit is appropriately attributed to all individuals involved in the project.%0D%0A%0D%0AI hope the experience of this internship helps you in your future career and gives you more understanding of what you want out of a work environment. """

    table_rows = [
            { "week_number": "0 - 1 week before",  "date": intake_start_date_object - timedelta(days=7), "subject": "1 week before WEHI internship", "body":body_before},
            { "week_number": "1 - First week", "date": intake_start_date_object - timedelta(days=7), "subject": "First week of WEHI internship", "body":body_first},
            { "week_number": "2 - Second week", "date": intake_start_date_object + timedelta(days=7), "subject": "Second week of WEHI internship", "body":body_second},
            { "week_number": "3 - Fourth week", "date": intake_start_date_object + timedelta(days=21), "subject": "Fourth week of WEHI internship", "body":body_fourth},
            { "week_number": "4 - Tenth week", "date": intake_start_date_object + timedelta(days=63), "subject": "Tenth week of WEHI internship", "body":body_tenth},
            { "week_number": "5 - End of internship", "date": intake_start_date_object + timedelta(days=91), "subject": "End of WEHI internship", "body":body_end}
           ]


    return table_rows

@app.route('/update_project_status', methods=['POST'])
def update_project_status():
    data = request.get_json()
    project_ids = data.get('project_ids', [])
    new_status = data.get('new_status')

    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()

    for name in project_ids:
        cursor.execute('UPDATE Projects SET status = ? WHERE name = ?', (new_status, name))

    conn.commit()
    conn.close()

    return jsonify({'status': 'success', 'message': 'Project statuses updated.'})

@app.route('/clean_pronouns', methods=['GET'])
def clean_pronouns():

    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('UPDATE Students SET pronouns = "she/her" WHERE pronouns in ("She/Her","She/her","she","She")')
    conn.commit()

    cursor.execute('UPDATE Students SET pronouns = "he/him" WHERE pronouns in ("He/him","He/Him","he","He","Mr")')
    conn.commit()

    # Close the database connection
    conn.close()

    return redirect(url_for('index'))


@app.route('/project_job_description/<int:project_id>', methods=['GET', 'POST'])
def project_job_description(project_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if request.method == 'POST':
        # Handle form submission and update all the Project Job Description fields
        about_organisation = request.form.get('about_organisation')
        position_title = request.form.get('position_title')
        position_description = request.form.get('position_description')
        skill_requirements = request.form.get('skill_requirements')
        about_org_word_min = int(request.form.get('about_org_word_min', 1))
        about_org_word_max = int(request.form.get('about_org_word_max', 70))
        position_desc_word_min = int(request.form.get('position_desc_word_min', 400))
        position_desc_word_max = int(request.form.get('position_desc_word_max', 500))
        skills_word_min = int(request.form.get('skills_word_min', 50))
        skills_word_max = int(request.form.get('skills_word_max', 70))

        try:
            # Update the project record for the current project
            cursor.execute('''UPDATE Projects 
                            SET skill_requirements = ?,
                                about_organisation = ?,
                                position_title = ?,
                                position_description = ?
                            WHERE id = ?''',
                            (skill_requirements, about_organisation, position_title, position_description, project_id))

            
            # Update global word limits for ALL projects in one go
            cursor.execute('''UPDATE Job_Description_Word_Count
                            SET about_org_word_min = ?,
                                about_org_word_max = ?,
                                position_desc_word_min = ?,
                                position_desc_word_max = ?,
                                skills_word_min = ?,
                                skills_word_max = ?''',
                            (about_org_word_min, about_org_word_max,
                            position_desc_word_min, position_desc_word_max,
                            skills_word_min, skills_word_max))

            conn.commit()
            print("DEBUG: Database commit successful")

        except Exception as e:
            print(f"DEBUG: Database error: {e}")
            conn.rollback()
        finally:
            conn.close()
        
        return redirect(url_for('projects_index'))

    # If it's a GET request, fetch the project data and word count settings
    cursor.execute('''SELECT name, about_organisation, position_title, position_description, skill_requirements
                        FROM Projects
                        WHERE id = ?''',
                    (project_id,))
    project_data = cursor.fetchone()

    cursor.execute('SELECT * FROM Job_Description_Word_Count')
    wordcount_data = cursor.fetchone()

    conn.close()

    return render_template(
        'project_job_description.html',
        project=project_data,
        wordcount=wordcount_data,
        project_id=project_id
    )

def insert_eng_interns_into_db(conn, data):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO students (
            full_name, email, mobile, 
            course, course_major, intake_id, status_id
        )           
        VALUES (?, ?, ?, ?, ?, ?, ? )
    ''', data)
    conn.commit()
    last_intern_id = cursor.lastrowid
    return last_intern_id

@app.route('/add_eng_interns', methods=['GET', 'POST'])
def add_eng_interns():
    if request.method == 'POST':
        data = request.form['student_data']
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM Intakes WHERE status = "new"')
        rows = cursor.fetchall()
        intake_id = rows[0][0]
        
        # FIXED: Get status_id for '01 Received application'
        cursor.execute('SELECT id FROM Statuses WHERE name = "01 Received application"')
        received_app_status_id = cursor.fetchone()[0]

        students_data = []
        lines = data.strip().split('\n')
        for line in lines:
            parts = line.split('|')
            email = parts[2].strip().split(' ')[0]
            mobile = ""
            student_tuple = (
                parts[0].strip(),  # full_name
                email,
                mobile,
                "Engineering and IT",
                parts[1].strip(),  # course_major
                intake_id,  # intake_id (integer) 
                received_app_status_id  # FIXED: status_id (integer)
            )
            students_data.append(student_tuple)
            insert_eng_interns_into_db(conn, student_tuple)

        conn.close()
        return redirect(url_for('new_applications'))

    return render_template('add_eng_interns.html')

if __name__ == '__main__':
    app.run(debug=True)

