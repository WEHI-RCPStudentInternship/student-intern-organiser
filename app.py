from flask import Flask, render_template, request, redirect, send_file, url_for,jsonify
import sqlite3
import os
import csv
import zipfile
import shutil
from datetime import datetime

from collections import Counter

app = Flask(__name__)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 300

 # Replace with your SQLite database file path
db_path = 'student_intern_data/student_intern_data.db' 

@app.route('/links/', methods=['GET'])
def links():
    return render_template('links.html')

# Allocating students projects
@app.route('/assigned_projects/', methods=['GET', 'PUT'])
def assigned_projects():
    # Connect to the SQLite database
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()
    try:
        if request.method == 'GET':
            # Fetch the projects from the Projects table
            cursor.execute('SELECT id, name FROM Projects ORDER BY status ASC, name ASC' )
            projects = cursor.fetchall()
            print(projects)

            cursor.execute('SELECT name FROM Intakes where status  = "new"')
            intake_current = cursor.fetchall()[0][0]

            cursor.execute('SELECT intern_id, full_name, project, pronouns, status, cover_letter_projects FROM Students WHERE intake = ?',(intake_current,))
            students = cursor.fetchall()

            cursor.execute('SELECT * FROM Statuses')
            statuses = cursor.fetchall()

            status_of_students_to_filter = [1,2,3,4,5,6,7,8,9,10,11,12,13,14]
            current_statuses_list = [row[1] for row in statuses if row[0] in status_of_students_to_filter]

            # Retrieve student data from the database
            # Prepare the SQL query with a placeholder for the statuses filter
            query = '''
                SELECT intern_id, full_name, project, pronouns, status, cover_letter_projects
                FROM Students
                WHERE intake = ? AND status IN ({})
            '''.format(','.join(['?'] * len(current_statuses_list)))


            # Execute the query with the statuses list
            cursor.execute(query, [intake_current] + current_statuses_list)
            students = cursor.fetchall()



            # Close the database connection
            cursor.close()
            conn.close()

            return render_template('Assigned_projects.html', projects=projects, students=students)
        elif request.method == 'PUT':
            # Handle the AJAX request for updating the student's project assignment
            data = request.get_json()
            intern_id = data['internId']
            new_project_id = data['projectId']

            # Update the student's project assignment in the database
            cursor.execute('UPDATE Students SET project = ? WHERE intern_id = ?', (new_project_id, intern_id))
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
        intern_id = data['internId']
        new_project_id = data['projectId']

        # Connect to the SQLite database
        conn = sqlite3.connect('student_intern_data/student_intern_data.db')
        cursor = conn.cursor()

        # Update the student's project assignment in the database
        cursor.execute('UPDATE Students SET project = ? WHERE intern_id = ?', (new_project_id, intern_id))
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
    cover_letter_projects = request.form.get('cover_letter_projects')
    Overall_External = request.form.get('Overall_External')
    Overall_Internal = request.form.get('Overall_Internal')
    learn_quickly_technical = request.form.get('learn_quickly_technical')
    learn_domain_concepts = request.form.get('learn_domain_concepts')
    Enthusiastic = request.form.get('Enthusiastic')
    Experience = request.form.get('Experience')
    Communication = request.form.get('Communication')
    Adaptability = request.form.get('Adaptability')
    summary_tech_skills = request.form.get('summary_tech_skills')
    summary_experience = request.form.get('summary_experience')


    # Connect to the SQLite database
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()

    # Update Students Evaluation data in the Students table
    cursor.execute('''
        UPDATE Students

        SET status = ?,
            pronunciation = ?,
            cover_letter_projects = ?,
            pre_internship_summary_recommendation_external = ?,
            pre_internship_summary_recommendation_internal = ?,
            pre_internship_technical_rating = ?,
            pre_internship_learning_quickly = ?,
            pre_internship_enthusiasm = ?,
            pre_internship_experience = ?,
            pre_internship_communication = ?,
            pre_internship_adaptable = ?,
            summary_tech_skills = ?,
            summary_experience = ?

        WHERE intern_id = ?
    ''', (status,pronunciation, cover_letter_projects, Overall_External, Overall_Internal,learn_quickly_technical, learn_domain_concepts, Enthusiastic, Experience, Communication, Adaptability,  summary_tech_skills, summary_experience, student_id))

    # Commit the changes and close the database connection
    conn.commit()
    conn.close()

    # Redirect to the student's evaluation  page in standardized vocabulary
    return redirect(url_for('pre_int_st_evaluation', intern_id=student_id))

@app.route('/pre_int_st_evaluation/<int:intern_id>', methods=['GET'])
def pre_int_st_evaluation(intern_id):
    # Connect to the SQLite database
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()

    # Retrieve the student's details from the database
    cursor.execute('SELECT * FROM Students WHERE intern_id = ?', (intern_id,))
    student = cursor.fetchone()

    # Close the database connection
    conn.close()
    pronoun = student[2]

    # Split the pronoun into multiple parts using the '/' delimiter 
    #he/him/his or she/her or they/them/their
    pronoun_parts = pronoun.split('/')

    # Assign pronoun1, pronoun2, and pronoun3 based on the pronoun_parts
    pronoun1 = pronoun_parts[0].strip()
    pronoun2 = pronoun_parts[1].strip() if len(pronoun_parts) > 1 else ""


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
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()

    # Retrieve the feedback data from the Students table
    cursor.execute('SELECT * FROM Students')
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
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
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
    return redirect(url_for('feedback_table', intern_id=student_id))
# feedback 
@app.route('/feedback/<int:intern_id>', methods=['GET'])
def feedback(intern_id):
    # Connect to the SQLite database
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()

    # Retrieve the student's details from the database
    cursor.execute('SELECT * FROM Students WHERE intern_id = ?', (intern_id,))
    student = cursor.fetchone()

    # Close the database connection
    conn.close()
    # Retrieve the pronoun from the database
    pronoun = student[2]
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
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()

    # Retrieve the feedback data from the Students table
    cursor.execute('SELECT * FROM Students')
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
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT full_name, pronunciation, project, status, mobile, email, start_date, end_date, hours_per_week, pronouns, pre_internship_summary_recommendation_internal FROM Students WHERE intern_id IN ({})'.format(','.join('?' for _ in student_ids)), student_ids)

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
        csv_writer.writerow(['Full Name', 'Pronunciation','Project','Status','Phone', 'Email', 'Start Date', 'End Date', 'Hours per Week','Pronouns','Summary pre-internship'])


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
    cursor.execute('UPDATE Students SET github_username = ?, full_name = ?, pronouns = ?, status = ?, email = ?, mobile = ?, course = ?, course_major = ?, intake = ?, project = ?, start_date = ?, end_date = ?, hours_per_week = ?, cover_letter_projects = ?, pronunciation = ?, post_internship_summary_rating_internal = ? WHERE intern_id = ?',
                   (data['github_username'], data['full_name'], data['pronouns'], data['status'], data['email'], data['mobile'], data['course'], data['course_major'], data['intake'], data['project'], data['start_date'], data['end_date'], data['hours_per_week'], data['cover_letter_projects'],data['pronunciation'],data['post_internship_summary_rating_internal'], intern_id))
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
            'github_username': request.form['github_username'],
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

@app.route('/share_students')
def share_students():
    # Connect to the SQLite database
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT name FROM Intakes where status  = "new"')
    intake_current = cursor.fetchall()[0][0]


    # Retrieve student data from the database
    cursor.execute('SELECT * FROM Statuses')
    statuses = cursor.fetchall()

    status_of_students_to_filter = [5,6]
    current_statuses_list = [row[1] for row in statuses if row[0] in status_of_students_to_filter]

    # Retrieve student data from the database
    # Prepare the SQL query with a placeholder for the statuses filter
    query = '''
        SELECT intern_id, full_name, email, mobile, intake, course, course_major , cover_letter_projects, pronunciation, summary_tech_skills, summary_experience, pre_internship_summary_recommendation_external, pre_internship_technical_rating || ' ' ||  pre_internship_learning_quickly || ' ' || pre_internship_enthusiasm || ' ' || pre_internship_experience || ' ' || pre_internship_communication || ' ' || pre_internship_adaptable AS student_details, github_username

        FROM Students
        WHERE intake = ? AND status IN ({})
    '''.format(','.join(['?'] * len(current_statuses_list)))


    # Execute the query with the statuses list
    cursor.execute(query, [intake_current] + current_statuses_list)
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
        csv_writer.writerow(['ID', 'Full Name', 'Email','Phone', 'Intake', 'Faculty', 'Course', 'Interested in Projects','Pronunciation','Tech Skills','Experience','Summary of Student','Details of Student','github username'])

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
    return send_file(zip_path, as_attachment=True, download_name=formatted_date+'_student_applications.zip')


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
    today = datetime.now()

    # Format the date as YYYY-mm-dd
    formatted_date = today.strftime("%Y-%m-%d")

    # Serve the ZIP file for download
    return send_file(zip_path, as_attachment=True, download_name=formatted_date+'_contract_files.zip')


@app.route('/import_redcap', methods=['GET', 'POST'])
def import_redcap():

    attachments_dir = 'student_intern_data/attachments'
    if request.method == 'POST':
        print(request.files)
        csv_file = request.files['csv_file']
        if csv_file:
            # Save the file to the attachments directory with the desired filename
            filename = str(intern_id)+"_"+full_name.replace(" ", "_").title()+"_signed_contract.pdf"

            file.save(os.path.join(attachments_dir, filename))
            # Get the referrer URL
            referrer = request.referrer

            # Redirect back to the previous page
            return redirect(referrer)
        zip_file = request.files['zip_file']
        if zip_file:
            filename = 'hello'
    
    return render_template('import_redcap.html')



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
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()


    cursor.execute('SELECT * FROM Projects')
    projects = cursor.fetchall()

    cursor.execute('SELECT name FROM Intakes where status  = "new"')
    intake_current = cursor.fetchall()[0][0]


    # Retrieve student data from the database
    cursor.execute('SELECT * FROM Statuses')
    statuses = cursor.fetchall()

    status_of_students_to_filter = [15,16,17,18,19,20,21]
    current_statuses_list = [row[1] for row in statuses if row[0] in status_of_students_to_filter]

    # Retrieve student data from the database
    # Prepare the SQL query with a placeholder for the statuses filter
    query = '''
        SELECT intern_id, full_name, email, pronunciation, project, intake, course, status, post_internship_summary_rating_internal
        FROM Students
        WHERE intake = ? AND status IN ({})
    '''.format(','.join(['?'] * len(current_statuses_list)))


    # Execute the query with the statuses list
    cursor.execute(query, [intake_current] + current_statuses_list)
    students = cursor.fetchall()

    # Close the database connection conn.close()
    title_of_page = "New Intake Unavailable"
    return render_template('index.html', students=students,statuses=statuses,title_of_page=title_of_page,projects=projects)


@app.route('/new_intake')
def index_new_intake():

    # Connect to the SQLite database
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()


    cursor.execute('SELECT * FROM Projects')
    projects = cursor.fetchall()

    cursor.execute('SELECT name FROM Intakes where status  = "new"')
    intake_current = cursor.fetchall()[0][0]


    # Retrieve student data from the database
    cursor.execute('SELECT * FROM Statuses')
    statuses = cursor.fetchall()

    status_of_students_to_filter = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19.20,21]
    current_statuses_list = [row[1] for row in statuses if row[0] in status_of_students_to_filter]

    # Retrieve student data from the database
    # Prepare the SQL query with a placeholder for the statuses filter
    query = '''
        SELECT intern_id, full_name, email, pronunciation, project, intake, course, status, post_internship_summary_rating_internal, pronouns,pre_internship_summary_recommendation_internal
        FROM Students
        WHERE intake = ? AND status IN ({})
    '''.format(','.join(['?'] * len(current_statuses_list)))


    # Execute the query with the statuses list
    cursor.execute(query, [intake_current] + current_statuses_list)
    students = cursor.fetchall()

    # Close the database connection conn.close()
    title_of_page = "New Intake All"
    return render_template('index.html', students=students,statuses=statuses,title_of_page=title_of_page,projects=projects)

@app.route('/outstanding')
def index_outstanding():
    # Connect to the SQLite database
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()


    cursor.execute('SELECT * FROM Projects')
    projects = cursor.fetchall()

    cursor.execute('SELECT name FROM Intakes where status  = "new"')
    intake_current = cursor.fetchall()[0][0]


    # Retrieve student data from the database
    cursor.execute('SELECT * FROM Statuses')
    statuses = cursor.fetchall()

    status_of_students_to_filter = [1,2,3,4,5,6,7,8]
    current_statuses_list = [row[1] for row in statuses if row[0] in status_of_students_to_filter]

    # Retrieve student data from the database
    # Prepare the SQL query with a placeholder for the statuses filter
    query = '''
        SELECT intern_id, full_name, email, pronunciation, project, intake, course, status, post_internship_summary_rating_internal, pronouns,pre_internship_summary_recommendation_internal
        FROM Students
        WHERE intake = ? AND status IN ({})
    '''.format(','.join(['?'] * len(current_statuses_list)))


    # Execute the query with the statuses list
    cursor.execute(query, [intake_current] + current_statuses_list)
    students = cursor.fetchall()


    # Close the database connection
    conn.close()
    title_of_page = "New Intake WIP"
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

    status_of_students_current = [13]
    current_statuses_list = [row[1] for row in statuses if row[0] in status_of_students_current]

    # Retrieve student data from the database
    # Prepare the SQL query with a placeholder for the statuses filter
    query = '''
        SELECT intern_id, full_name, email, pronunciation, project, intake, course, status, post_internship_summary_rating_internal, pronouns,pre_internship_summary_recommendation_internal
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
    cursor.execute('SELECT intern_id, full_name, email, pronunciation, project, intake, course, status, post_internship_summary_rating_internal, pronouns,pre_internship_summary_recommendation_internal FROM Students')
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


def change_post_internship_rating(student_ids, new_post_internship_rating):
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
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
    ratings = [student[42] for student in students if student[42] is not None ]

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


@app.route('/dashboard/<string:dashboard_type>',methods=['GET'])
def dashboard(dashboard_type):
    print(dashboard_type)
    # Connect to the SQLite database
    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
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
                        pronoun_percentage=pronoun_percentage,breakdown_statuses=breakdown_statuses,total_students_current_and_past = total_students_current_and_past)



if __name__ == '__main__':
    app.run(debug=True)
