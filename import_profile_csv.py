import csv
import sqlite3
import sys
import zipfile
import shutil
import pandas as pd
"""
    Usage : python import_csv_from_redcap.py <csvfile> <zipfile>

    Usage : python import_csv_from_redcap.py TestStudentInternshi_DATA_LABELS_2023-06-27_1517.csv FilesReport_AllDataAllRecordsAnd_2023-06-27_1518.zip

"""



def read_csv_file(csv_file_path):
    df = pd.read_csv(csv_file_path)

    print(df)

    for index, row in df.iterrows():
        user_id = row[0]
        student_name = row[1]
        email = row[2]
        profile = row[3]

        
