import csv
import random

# Generate dummy data for 20 students
students = []
for i in range(1, 21):
    student = [
        f"Full Name {i}",  # full_name
        f"Pronouns {i}",  # pronouns
        f"Status {i}",  # status
        f"email{i}@example.com",  # email
        f"123456789{i}",  # mobile
        f"Course {i}",  # course
        f"Course Major {i}",  # course_major
        f"Application Doc {i}",  # link_to_application_doc
        f"Read Handbook {i}",  # read_student_handbook
        f"Read Projects {i}",  # read_student_projects
        f"Cover Letter Projects {i}",  # cover_letter_projects
        f"Cover Letter Concept {i}",  # cover_letter_concept
        f"Cover Letter Technical {i}",  # cover_letter_technical
        f"Pronunciation {i}",  # pronunciation
        f"Project {i}",  # project
        "2023-06-01",  # start_date
        "2023-06-30",  # end_date
        random.randint(10, 30),  # hours_per_week
        f"Intake {i}",  # intake
        f"supervisor{i}@example.com",  # supervisor_email
        f"wehi{i}@example.com",  # wehi_email
        f"Tech Skills {i}",  # summary_tech_skills
        f"Experience {i}",  # summary_experience
        f"Interest in Projects {i}",  # summary_interest_in_projects
        f"Recommendation External {i}",  # pre_internship_summary_recommendation_external
        f"Recommendation Internal {i}",  # pre_internship_summary_recommendation_internal
        f"Technical Rating {i}",  # pre_internship_technical_rating
        f"Social Rating {i}",  # pre_internship_social_rating
        f"Learning Quickly {i}",  # pre_internship_learning_quickly
        f"Enthusiasm {i}",  # pre_internship_enthusiasm
        f"Experience {i}",  # pre_internship_experience
        f"Communication {i}",  # pre_internship_communication
        f"Adaptable {i}",  # pre_internship_adaptable
        f"Problem Solver {i}",  # pre_internship_problem_solver
        f"Comments {i}",  # post_internship_comments
        f"Adaptability {i}",  # post_internship_adaptability
        f"Learn Technical {i}",  # post_internship_learn_technical
        f"Learn Conceptual {i}",  # post_internship_learn_conceptual
        f"Collaborative {i}",  # post_internship_collaborative
        f"Ambiguity {i}",  # post_internship_ambiguity
        f"Complexity {i}",  # post_internship_complexity
        f"Summary Rating Internal {i}",  # post_internship_summary_rating_internal
        f"Summary Rating External {i}"  # post_internship_summary_rating_external
    ]
    students.append(student)

# Save data to a CSV file
csv_file = 'students.csv'
header = [
    'full_name',
    'pronouns',
    'status',
    'email',
    'mobile',
    'course',
    'course_major',
    'link_to_application_doc',
    'read_student_handbook',
    'read_student_projects',
    'cover_letter_projects',
    'cover_letter_concept',
    'cover_letter_technical',
    'pronunciation',
    'project',
    'start_date',
    'end_date',
    'hours_per_week',
    'intake',
    'supervisor_email',
    'wehi_email',
    'summary_tech_skills',
    'summary_experience',
    'summary_interest_in_projects',
    'pre_internship_summary_recommendation_external',
    'pre_internship_summary_recommendation_internal',
    'pre_internship_technical_rating',
    'pre_internship_social_rating',
    'pre_internship_learning_quickly',
    'pre_internship_enthusiasm',
    'pre_internship_experience',
    'pre_internship_communication',
    'pre_internship_adaptable',
    'pre_internship_problem_solver',
    'post_internship_comments',
    'post_internship_adaptability',
    'post_internship_learn_technical',
    'post_internship_learn_conceptual',
    'post_internship_collaborative',
    'post_internship_ambiguity',
    'post_internship_complexity',
    'post_internship_summary_rating_internal',
    'post_internship_summary_rating_external'
]

with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(header)
    writer.writerows(students)

print(f"CSV file '{csv_file}' has been generated.")

