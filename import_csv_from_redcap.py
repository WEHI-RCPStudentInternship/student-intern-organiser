import csv
import sqlite3
import sys
import zipfile
import shutil

"""
    Usage : python import_csv_from_redcap.py <csvfile> <zipfile>

    Usage : python import_csv_from_redcap.py TestStudentInternshi_DATA_LABELS_2023-06-27_1517.csv FilesReport_AllDataAllRecordsAnd_2023-06-27_1518.zip

"""


def extract_pdf_files(zip_file_path, students_inserted, output_directory):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        for file_info in zip_ref.infolist():
            if file_info.filename.endswith('.pdf'):
                extracted_path = zip_ref.extract(file_info, output_directory)
                split_text = extracted_path.split("/")
                last_element = split_text[-1]
                try:
                    final_file_name = students_inserted[last_element]
                    destination_path = 'student_intern_data/attachments/'+ final_file_name
                    shutil.move(extracted_path, destination_path)
                except:
                    continue

    # clean up output_directory
    try:
        shutil.rmtree(output_directory)
    except:
        print('Error deleting directory')




def read_csv_file(file_path,zip_file_path):

    conn = sqlite3.connect('student_intern_data/student_intern_data.db')
    cursor = conn.cursor()
    cursor.execute('Select name from intakes where status = "new";')
    rows = cursor.fetchall()
    intake = rows[0][0]

    cursor.execute('Select redcap_id from students where intake = ?;',[intake])
    rows = cursor.fetchall()
    redcap_ids = [row[0] for row in rows]
    print(redcap_ids)

    with open(file_path, 'r') as csv_file:
        reader = csv.reader(csv_file)
        header = next(reader) 

        # Provide the path to the zip file and the output directory
        output_directory = 'student_intern_data/import/temp.'

        students_inserted = {}

        for row in reader:
            redcap_id = str(row[0])

            if redcap_id not in redcap_ids:

                full_name = row[10]
                pronouns = row[11]
                email_address = row[12]
                mobile_number = row[13]
                faculty_info = row[14]
                course_name = row[15]
                

                summary_interest_in_projects = ''
                if row[16] == 'Checked':
                    summary_interest_in_projects += 'Data Analytics,'
                if row[17] == 'Checked':
                    summary_interest_in_projects += 'Data Engineering,'
                if row[18] == 'Checked':
                    summary_interest_in_projects += 'Software Engineering,'
                if row[19] == 'Checked':
                    summary_interest_in_projects += 'Web Development'
                summary_interest_in_projects = summary_interest_in_projects.rstrip(',')

                status = '01 Received application'
                github_username = row[20]
                project = 'Unassigned'
                
                data = (
                    full_name, pronouns, email_address, mobile_number,
                    faculty_info, course_name, summary_interest_in_projects, intake, status, github_username, project, str(redcap_id)
                )
                intern_id = insert_student_data(conn, data)

                extracted_zip_file_name = str(redcap_id)+'_fm_cletter_resume_v2.pdf' 
                final_file_name = str(intern_id) + "_"+full_name.replace(" ", "_")+"_application.pdf"
                students_inserted[extracted_zip_file_name] = final_file_name

            else:
                continue

        # Call the function to extract the PDF files
        extract_pdf_files(zip_file_path, students_inserted, output_directory)

def insert_student_data(conn, data):
    cursor = conn.cursor()

    # Insert data into the students table
    cursor.execute('''
        INSERT INTO students (
            full_name, pronouns, email, mobile,
            course, course_major, summary_interest_in_projects,intake, status, github_username,project,redcap_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?)
    ''', data)
    conn.commit()

    last_intern_id = cursor.lastrowid
    return last_intern_id



# Provide the path to your CSV file
#csv_file_path = sys.argv[1]
#zip_file_path = sys.argv[2]
#read_csv_file(csv_file_path,zip_file_path)
