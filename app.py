from flask import Flask, render_template, request, redirect, send_file
import sqlite3
import os
import csv
import zipfile
import shutil
from datetime import datetime

from collections import Counter

app = Flask(__name__)


app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 300

db_path = 'student_intern_data/student_intern_data.db'  # Replace with your SQLite database file path

@app.route('/download_key_attributes')
def download_key_attributes():
    data = request.args.getlist('student_ids')
    values = data[0].split(',')

    student_ids = [int(value) for value in values] 


 
    # Connect to the SQLite database
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT full_name, project, status, mobile, email, start_date, end_date, hours_per_week FROM Students WHERE intern_id IN ({})'.format(','.join('?' for _ in student_ids)), student_ids)

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
        csv_writer.writerow(['Full Name', 'Project','Status','Phone', 'Email', 'Start Date', 'End Date', 'Hours per Week'])


        for student in students:
            # Retrieve student data from the database
            # Write the student data to the CSV file
            csv_writer.writerow(student)



    return send_file(csv_path, as_attachment=True)

 
def get_statuses():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM Statuses')
    statuses = [row[0] for row in cursor.fetchall()]
    conn.close()
    return statuses

def get_intakes():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM Intakes')
    intakes = [row[0] for row in cursor.fetchall()]
    conn.close()
    return intakes

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
    cursor.execute('SELECT * FROM Students WHERE intern_id = ?', (intern_id,))
    student = cursor.fetchone()
    conn.close()
    return student

def update_student(intern_id, data):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('UPDATE Students SET full_name = ?, pronouns = ?, status = ?, email = ?, mobile = ?, course = ?, course_major = ?, intake = ?, project = ?, start_date = ?, end_date = ?, hours_per_week = ?, cover_letter_projects = ?, pronunciation = ?, post_internship_summary_rating_internal = ? WHERE intern_id = ?',
                   (data['full_name'], data['pronouns'], data['status'], data['email'], data['mobile'], data['course'], data['course_major'], data['intake'], data['project'], data['start_date'], data['end_date'], data['hours_per_week'], data['cover_letter_projects'],data['pronunciation'],data['post_internship_summary_rating_internal'], intern_id))
    conn.commit()
    conn.close()

@app.route('/edit_student/<int:intern_id>', methods=['GET', 'POST'])
def edit_student(intern_id):
    if request.method == 'POST':
        # Handle form submission and update the student record in the database
        print(request.form)
        data = {
            'full_name': request.form['full_name'],
            'pronouns': request.form['pronouns'],
            'status': request.form['status'],
            'email': request.form['email'],
            'mobile': request.form['mobile'],
            'course': request.form['course'],
            'course_major': request.form['course_major'],
            'intake': request.form['intake'],
            'project': request.form['project'],
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

@app.route('/download_contracts_and_applications')
def download_contracts_and_applications():
    # Connect to the SQLite database
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()

    # Retrieve students with status '09 Signed contract' from the database
    cursor.execute('SELECT intern_id, full_name FROM Students WHERE status = ?', ('09 Signed contract',))
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
        csv_writer.writerow(['Full Name', 'Phone', 'Email', 'Start Date', 'End Date', 'Hours per Week'])

        for student in students:
            # Retrieve student data from the database
            cursor.execute('SELECT full_name, mobile, email, start_date, end_date, hours_per_week FROM Students WHERE intern_id = ?', (student[0],))
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
    today = datetime.date.today()

    # Format the date as YYYY-mm-dd
    formatted_date = today.strftime("%Y-%m-%d")

    # Serve the ZIP file for download
    return send_file(zip_path, as_attachment=True, attachment_filename=formatted_date+'_contract_files.zip')




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




@app.route('/current_intake')
def index_current_intake():
    # Connect to the SQLite database
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()

    # Retrieve student data from the database
    cursor.execute('SELECT * FROM Statuses')
    statuses = cursor.fetchall()

    cursor.execute('SELECT * FROM Projects')
    projects = cursor.fetchall()

    cursor.execute('SELECT name FROM Intakes where current = "yes"')
    intake_current = cursor.fetchall()[0][0]


    # Retrieve student data from the database
    # Prepare the SQL query with a placeholder for the statuses filter
    cursor.execute('SELECT intern_id, full_name, email, pronunciation, project, intake, course, status, post_internship_summary_rating_internal FROM Students WHERE intake = ?',(intake_current,))

    students = cursor.fetchall()

    # Close the database connection
    conn.close()
    title_of_page = "Current Recruitment for this Intake"
    return render_template('index.html', students=students,statuses=statuses,title_of_page=title_of_page,projects=projects)

@app.route('/outstanding')
def index_outstanding():
    # Connect to the SQLite database
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()


    cursor.execute('SELECT * FROM Projects')
    projects = cursor.fetchall()


    # Retrieve student data from the database
    cursor.execute('SELECT * FROM Statuses')
    statuses = cursor.fetchall()

    status_of_students_current_and_past = [1,2,3,4,5,6,7,8,19,21]
    current_statuses_list = [row[1] for row in statuses if row[0] in status_of_students_current_and_past]

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
    title_of_page = "Available Students"
    return render_template('index.html', students=students,statuses=statuses,title_of_page=title_of_page,projects=projects)



@app.route('/current')
def index_current():
    # Connect to the SQLite database
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()

    # Retrieve student data from the database
    cursor.execute('SELECT * FROM Statuses')
    statuses = cursor.fetchall()

    cursor.execute('SELECT * FROM Projects')
    projects = cursor.fetchall()

    status_of_students_current_and_past = [9, 10,11,12,13]
    current_statuses_list = [row[1] for row in statuses if row[0] in status_of_students_current_and_past]

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
    return render_template('index.html', students=students,statuses=statuses,title_of_page=title_of_page,projects=projects)


@app.route('/')
def index():
    # Connect to the SQLite database
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()

    # Retrieve student data from the database
    cursor.execute('SELECT intern_id, full_name, email, pronunciation, project, intake, course, status,post_internship_summary_rating_internal FROM Students')
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

@app.route('/change_project', methods=['POST'])
def change_project():

    data = request.get_json()
    student_ids = data.get('student_ids', [])
    new_project = data.get('new_project', '')

    # Convert student IDs to integers
    student_ids = [int(id) for id in student_ids]

    # Call the change_student_project function
    change_student_project(student_ids, new_project)

    # Redirect back to the index page
    return redirect('/')


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



def change_student_project(student_ids, new_project):
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()

    # Prepare the SQL query
    query = '''
        UPDATE Students
        SET project = ?
        WHERE intern_id IN ({})
    '''.format(','.join(['?'] * len(student_ids)))

    # Execute the query
    cursor.execute(query, [new_project] + student_ids)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


def calculate_breakdown_of_students(students):
    ratings = [student[42] for student in students if student[42] is not None and student[42] != 'N/A']

    # Calculate the value breakdown using Counter
    breakdown_ratings = dict(Counter(ratings))
    total_students = len(ratings)


    courses = [student[6] for student in students]

    # Calculate the value breakdown using Counter
    breakdown_courses = dict(Counter(courses))


    statuses = [student[3] for student in students]
    breakdown_statuses = dict(Counter(statuses))
    print(breakdown_statuses)

    return [breakdown_ratings,breakdown_courses,total_students,breakdown_statuses]

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


@app.route('/dashboard')
def dashboard():
    # Connect to the SQLite database
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()

    # Retrieve student data from the database
    cursor.execute('SELECT * FROM Statuses')
    statuses = cursor.fetchall()

    status_of_students_current_and_past = [9, 10, 11, 12, 13, 14]
    current_statuses_list = [row[1] for row in statuses if row[0] in status_of_students_current_and_past]

    # Retrieve student data from the database
    # Prepare the SQL query with placeholders for the statuses filter and pronouns
    query = '''
        SELECT *
        FROM Students
        WHERE status IN ({}) AND pronouns IS NOT NULL
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
    total_students = result[2]
    breakdown_statuses = result[3]

    pronoun_data, pronoun_percentage, total_students = calculate_breakdown_of_pronouns(students)

    return render_template('dashboard.html', students=students, breakdown_ratings=breakdown_ratings,
                        breakdown_courses=breakdown_courses, 
                        total_students=total_students, pronoun_data=pronoun_data,
                        pronoun_percentage=pronoun_percentage,breakdown_statuses=breakdown_statuses)



if __name__ == '__main__':
    app.run(debug=True)

