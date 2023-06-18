from flask import Flask, render_template, request, redirect
import sqlite3

from collections import Counter

app = Flask(__name__)

@app.route('/current')
def index_current():
    # Connect to the SQLite database
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()

    # Retrieve student data from the database
    cursor.execute('SELECT * FROM Statuses')
    statuses = cursor.fetchall()

    print(statuses)
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

    return render_template('index.html', students=students,statuses=statuses)


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

    return render_template('index.html', students=students,statuses=statuses)

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

    return render_template('view.html', student=student)


@app.route('/change_status', methods=['POST'])
def change_status():

    data = request.get_json()
    student_ids = data.get('student_ids', [])
    new_status = data.get('new_status', '')

    print(student_ids)
    print(new_status)


    # Convert student IDs to integers
    student_ids = [int(id) for id in student_ids]

    # Call the change_student_status function
    change_student_status(student_ids, new_status)

    # Redirect back to the index page
    return redirect('/')

def change_student_status(student_ids, new_status):
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()

    print(student_ids)
    print(new_status) 

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

@app.route('/dashboard')
def dashboard():
    # Connect to the SQLite database
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()

    # Retrieve student data from the database
    cursor.execute('SELECT * FROM Students where status = "14 Finished"')
    students = cursor.fetchall()

    item_values = [student[42] for student in students]
    # Calculate the value breakdown using Counter
    breakdown_ratings = dict(Counter(item_values))
    total_students = len(students)

    item_values = [student[6] for student in students]

    # Calculate the value breakdown using Counter
    breakdown_courses = dict(Counter(item_values))

    total_equivalent = 0
    for value, count in breakdown_courses.items():
        total_equivalent = total_equivalent + (9000 * count if value == "Engineering" else count * 3000)



    # Close the database connection
    conn.close()

    return render_template('dashboard.html', students=students,breakdown_ratings=breakdown_ratings,breakdown_courses=breakdown_courses,total_equivalent=total_equivalent,total_students=total_students)

if __name__ == '__main__':
    app.run(debug=True)

