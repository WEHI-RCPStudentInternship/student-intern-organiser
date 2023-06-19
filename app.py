from flask import Flask, render_template, request, redirect, send_file
import sqlite3
import os

from collections import Counter

app = Flask(__name__)

@app.route('/current_intake')
def index_current_intake():
    # Connect to the SQLite database
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()

    # Retrieve student data from the database
    cursor.execute('SELECT * FROM Statuses')
    statuses = cursor.fetchall()

    cursor.execute('SELECT name FROM Intakes where current = "yes"')
    intake_current = cursor.fetchall()[0][0]


    # Retrieve student data from the database
    # Prepare the SQL query with a placeholder for the statuses filter
    cursor.execute('SELECT intern_id, full_name, email, pronunciation, project, intake, course, status, post_internship_summary_rating_internal FROM Students WHERE intake = ?',(intake_current,))

    students = cursor.fetchall()

    # Close the database connection
    conn.close()
    title_of_page = "Current Recruitment for this Intake"
    return render_template('index.html', students=students,statuses=statuses,title_of_page=title_of_page)

@app.route('/outstanding')
def index_outstanding():
    # Connect to the SQLite database
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()

    # Retrieve student data from the database
    cursor.execute('SELECT * FROM Statuses')
    statuses = cursor.fetchall()

    rows_to_extract = [1,2,3,4,5,6,7,8,19,21]
    current_statuses_list = [row[1] for row in statuses if row[0] in rows_to_extract]

    # Retrieve student data from the database
    # Prepare the SQL query with a placeholder for the statuses filter
    query = '''
        SELECT intern_id, full_name, email, pronunciation, project, intake, course, status, post_internship_summary_rating_internal
        FROM Students
        WHERE status IN ({})
    '''.format(','.join(['?'] * len(current_statuses_list)))

    # Execute the query with the statuses list
    cursor.execute(query, current_statuses_list)

    students = cursor.fetchall()


    # Close the database connection
    conn.close()
    title_of_page = "Outstanding Students"
    return render_template('index.html', students=students,statuses=statuses,title_of_page=title_of_page)



@app.route('/current')
def index_current():
    # Connect to the SQLite database
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()

    # Retrieve student data from the database
    cursor.execute('SELECT * FROM Statuses')
    statuses = cursor.fetchall()

    rows_to_extract = [9, 10,11,12,13]
    current_statuses_list = [row[1] for row in statuses if row[0] in rows_to_extract]

    # Retrieve student data from the database
    # Prepare the SQL query with a placeholder for the statuses filter
    query = '''
        SELECT intern_id, full_name, email, pronunciation, project, intake, course, status, post_internship_summary_rating_internal
        FROM Students
        WHERE status IN ({})
    '''.format(','.join(['?'] * len(current_statuses_list)))

    # Execute the query with the statuses list
    cursor.execute(query, current_statuses_list)

    students = cursor.fetchall()


    # Close the database connection
    conn.close()
    title_of_page = "Currently Signed Students"
    return render_template('index.html', students=students,statuses=statuses,title_of_page=title_of_page)


@app.route('/')
def index():
    # Connect to the SQLite database
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()

    # Retrieve student data from the database
    cursor.execute('SELECT intern_id, full_name, email, pronunciation, project, intake, course, status,post_internship_summary_rating_internal FROM Students')
    students = cursor.fetchall()

    # Retrieve student data from the database
    cursor.execute('SELECT * FROM Statuses')
    statuses = cursor.fetchall()

    # Close the database connection
    conn.close()
    title_of_page = "All Students"
    return render_template('index.html', students=students,statuses=statuses,title_of_page=title_of_page)

# Route to serve the file from a different directory
@app.route('/view_docs/<path:filename>')
def view_docs(filename):
    directory = 'student_intern_data/attachments/'  # Replace with the actual directory path
    filepath = directory + '/' + filename
    return send_file(filepath, as_attachment=True)

@app.route('/view/<int:intern_id>')
def student(intern_id):
    # Connect to the SQLite database
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()

    # Retrieve student data from the database
    cursor.execute('SELECT * FROM Students WHERE intern_id = ?', (intern_id,))
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


@app.route('/change_status', methods=['POST'])
def change_status():

    data = request.get_json()
    student_ids = data.get('student_ids', [])
    new_status = data.get('new_status', '')


    # Convert student IDs to integers
    student_ids = [int(id) for id in student_ids]

    # Call the change_student_status function
    change_student_status(student_ids, new_status)

    # Redirect back to the index page
    return redirect('/')

def change_student_status(student_ids, new_status):
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()

    # Prepare the SQL query
    query = '''
        UPDATE Students
        SET status = ?
        WHERE intern_id IN ({})
    '''.format(','.join(['?'] * len(student_ids)))

    # Execute the query
    cursor.execute(query, [new_status] + student_ids)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


def calculate_breakdown_of_students(students):
    item_values = [student[42] for student in students]
    item_values = [student[42] for student in students if student[42] is not None]

    # Calculate the value breakdown using Counter
    breakdown_ratings = dict(Counter(item_values))
    total_students = len(item_values)

    item_values = [student[6] for student in students]

    # Calculate the value breakdown using Counter
    breakdown_courses = dict(Counter(item_values))

    total_equivalent = 0
    for value, count in breakdown_courses.items():
        total_equivalent = total_equivalent + (9000 * count if value == "Engineering" else count * 3000)


    return [breakdown_ratings,breakdown_courses,total_equivalent,total_students]


@app.route('/dashboard')
def dashboard():
    # Connect to the SQLite database
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()

    # Retrieve student data from the database
    cursor.execute('SELECT * FROM Statuses')
    statuses = cursor.fetchall()

    rows_to_extract = [9, 10,11,12,13,14]
    current_statuses_list = [row[1] for row in statuses if row[0] in rows_to_extract]

    # Retrieve student data from the database
    # Prepare the SQL query with a placeholder for the statuses filter
    query = '''
        SELECT *
        FROM Students
        WHERE status IN ({})
    '''.format(','.join(['?'] * len(current_statuses_list)))

    # Execute the query with the statuses list
    cursor.execute(query, current_statuses_list)

    # Retrieve student data from the database
    students = cursor.fetchall()

    # Close the database connection
    conn.close()

    result = calculate_breakdown_of_students(students)

    breakdown_ratings = result[0]
    breakdown_courses = result[1]
    total_equivalent = result[2]
    total_students = result[3]

    return render_template('dashboard.html', students=students,breakdown_ratings=breakdown_ratings,breakdown_courses=breakdown_courses,total_equivalent=total_equivalent,total_students=total_students)

if __name__ == '__main__':
    app.run(debug=True)

