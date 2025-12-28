<<<<<<< HEAD
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE Students (
        intern_id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        pronouns TEXT,
        status TEXT,
        status_id INTEGER,
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
        intake_id INTEGER,
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
        github_username TEXT,
        extra_notes TEXT,
        remote_internship TEXT,
        code_of_conduct TEXT,
        facilitator_follower TEXT,
        listener_or_talker TEXT,
        thinker_brainstormer TEXT,
        why_applied TEXT,
        projects_recommended TEXT,
        -- NEW: Foreign key constraints
        FOREIGN KEY (status_id) REFERENCES Statuses(id),
        FOREIGN KEY (intake_id) REFERENCES Intakes(id)
    );
CREATE TABLE Statuses (
        id INTEGER PRIMARY KEY,
        name TEXT
    );
CREATE TABLE IF NOT EXISTS "Intakes" (
            id INTEGER PRIMARY KEY,
            name TEXT,
            status TEXT
        , science_start_date date, engit_start_date date);
CREATE TABLE Projects
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, status INT);
=======
-- new schema with new foreign key fields 
CREATE TABLE Students_new ( 
        intern_id INTEGER PRIMARY KEY AUTOINCREMENT, 
        full_name TEXT, 
        pronouns TEXT, 
        status TEXT, 
        status_id INTEGER,  -- new status field for status table association
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
        project_id INTEGER, -- new project field for project table association 
        start_date DATE, 
        end_date DATE, 
        hours_per_week INTEGER, 
        intake TEXT, 
        intake_id INTEGER,  -- new intake field for intake table association
        supervisor_email TEXT, 
        wehi_email TEXT, 
        summary_tech_skills TEXT, 
        summary_experience TEXT, 
        summary_interest_in_projects TEXT, 
        pre_internship_summary_recommendation_external TEXT, 
        pre_internship_summary_recommendation_internal TEXT, 
        pre_internship_internal_eval_level_id INTEGER,  -- new field for internal skills association 
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
        post_internship_summary_rating_external TEXT, 
        github_username, extra_notes text, 
        remote_internship TEXT, 
        code_of_conduct TEXT, 
        facilitator_follower TEXT, 
        listener_or_talker TEXT, 
        thinker_brainstormer TEXT, 
        why_applied TEXT, 
        projects_recommended TEXT, 
        redcap_id TEXT,
        show_key_skill TEXT, 
        -- NEW: Foreign key constraints 
        FOREIGN KEY (status_id) REFERENCES Statuses(id), 
        FOREIGN KEY (project_id) REFERENCES Projects(id), 
        FOREIGN KEY (intake_id) REFERENCES Intakes(id), 
        FOREIGN KEY (pre_internship_internal_eval_level_id) REFERENCES Internal_eval_levels(id) 
        ); 

-- insert existing data from original to new database 

INSERT INTO Students_new ( 
        intern_id, 
        full_name, 
        pronouns, 
        status, 
        email, 
        mobile, 
        course, 
        course_major, 
        link_to_application_doc, 
        read_student_handbook, 
        read_student_projects, 
        cover_letter_projects, 
        cover_letter_concept, 
        cover_letter_technical, 
        pronunciation, 
        project, 
        start_date, 
        end_date, 
        hours_per_week, 
        intake, 
        supervisor_email, 
        wehi_email, 
        summary_tech_skills, 
        summary_experience, 
        summary_interest_in_projects, 
        pre_internship_summary_recommendation_external, 
        pre_internship_summary_recommendation_internal, 
        pre_internship_technical_rating, 
        pre_internship_social_rating, 
        pre_internship_learning_quickly, 
        pre_internship_enthusiasm, 
        pre_internship_experience, 
        pre_internship_communication, 
        pre_internship_adaptable, 
        pre_internship_problem_solver, 
        post_internship_comments, 
        post_internship_adaptability, 
        post_internship_learn_technical, 
        post_internship_learn_conceptual, 
        post_internship_collaborative, 
        post_internship_ambiguity, 
        post_internship_complexity, 
        post_internship_summary_rating_internal, 
        post_internship_summary_rating_external, 
        github_username, extra_notes, 
        remote_internship, 
        code_of_conduct, 
        facilitator_follower, 
        listener_or_talker, 
        thinker_brainstormer, 
        why_applied, 
        projects_recommended, 
        redcap_id,
        show_key_skill) 
SELECT intern_id, 
        full_name, 
        pronouns, 
        status, 
        email, 
        mobile, 
        course, 
        course_major, 
        link_to_application_doc, 
        read_student_handbook, 
        read_student_projects, 
        cover_letter_projects, 
        cover_letter_concept, 
        cover_letter_technical, 
        pronunciation, 
        project, 
        start_date, 
        end_date, 
        hours_per_week, 
        intake, 
        supervisor_email, 
        wehi_email, 
        summary_tech_skills, 
        summary_experience, 
        summary_interest_in_projects, 
        pre_internship_summary_recommendation_external, 
        pre_internship_summary_recommendation_internal, 
        pre_internship_technical_rating, 
        pre_internship_social_rating, 
        pre_internship_learning_quickly, 
        pre_internship_enthusiasm, 
        pre_internship_experience, 
        pre_internship_communication, 
        pre_internship_adaptable, 
        pre_internship_problem_solver, 
        post_internship_comments, 
        post_internship_adaptability, 
        post_internship_learn_technical, 
        post_internship_learn_conceptual, 
        post_internship_collaborative, 
        post_internship_ambiguity, 
        post_internship_complexity, 
        post_internship_summary_rating_internal, 
        post_internship_summary_rating_external, 
        github_username, extra_notes, 
        remote_internship, 
        code_of_conduct, 
        facilitator_follower, 
        listener_or_talker, 
        thinker_brainstormer, 
        why_applied, 
        projects_recommended, 
        redcap_id,
        show_key_skill 
FROM Students; 

-- add corresponding value to new fields
UPDATE Students_new
SET status_id = 
        (SELECT statuses.id FROM statuses
        WHERE statuses.name = students_new.status);

UPDATE Students_new
SET project_id = 
        (SELECT projects.id FROM projects
        WHERE projects.name = students_new.project);

UPDATE Students_new
SET intake_id = 
        (SELECT intakes.id FROM intakes
        WHERE intakes.name = students_new.intake);

UPDATE Students_new
SET pre_internship_internal_eval_level_id =
        (SELECT Internal_eval_levels.id FROM Internal_eval_levels
        WHERE SUBSTR(
                students_new.pre_internship_summary_recommendation_internal, 
                INSTR(students_new.pre_internship_summary_recommendation_internal, '-') + 2
                ) 
        = Internal_eval_levels.name);

-- drop old database
ALTER TABLE Students RENAME TO Students_old;
ALTER TABLE Students_new RENAME TO Students;
-- UNCOMMENT LATER
-- DROP TABLE Students_old
>>>>>>> project-internal-normalisation
