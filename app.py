from flask import Flask, render_template
import sqlite3

from collections import Counter

app = Flask(__name__)

@app.route('/')
def index():
    # Connect to the SQLite database
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()

    # Retrieve student data from the database
    cursor.execute('SELECT intern_id, full_name, email, pronunciation, project, intake, course, status,post_internship_summary_rating_internal FROM Students')
    students = cursor.fetchall()

    # Close the database connection
    conn.close()

    return render_template('index.html', students=students)

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

@app.route('/dashboard')
def dashboard():
    # Connect to the SQLite database
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()

    # Retrieve student data from the database
    cursor.execute('SELECT * FROM Students')
    students = cursor.fetchall()

    item_values = [student[42] for student in students]

    # Calculate the value breakdown using Counter
    breakdown_ratings = dict(Counter(item_values))

    item_values = [student[6] for student in students]

    # Calculate the value breakdown using Counter
    breakdown_courses = dict(Counter(item_values))

    # Close the database connection
    conn.close()

    return render_template('dashboard.html', students=students,breakdown_ratings=breakdown_ratings,breakdown_courses=breakdown_courses)

if __name__ == '__main__':
    app.run(debug=True)

