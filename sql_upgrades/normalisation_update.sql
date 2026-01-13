-- Create the Internal_eval_levels table if it doesn't exist
CREATE TABLE IF NOT EXISTS Internal_eval_levels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
);

INSERT INTO Internal_eval_levels (name)
VALUES ('F Translator - Recommend sign up even without a project. '),
        ('F Sysadmin - Recommend sign up even without a project. '),
        ('F ETS/Fast Learner - Recommend sign up even without a project. '),
        ('F Technical Skills - Recommend sign up for a specific project. '),
        ('Translator - Recommend sign up even without a project. '),
        ('Sysadmin - Recommend sign up even without a project. '),
        ('ETS/Fast learner - Recommend sign up for a specific project. '),
        ('TS - Recommend no sign up except under specific circumstances. ');



-- Enable foreign key enforcement
PRAGMA foreign_keys = ON;
-- Add new foreign key fields
ALTER TABLE Students ADD COLUMN project_id INTEGER REFERENCES Projects(id) DEFAULT NULL;
ALTER TABLE Students ADD COLUMN status_id INTEGER REFERENCES Statuses(id) DEFAULT NULL;
ALTER TABLE Students ADD COLUMN intake_id INTEGER REFERENCES Intakes(id) DEFAULT NULL;
ALTER TABLE Students ADD COLUMN pre_internship_internal_eval_level_id INTEGER REFERENCES internal_eval_levels(id) DEFAULT NULL;


-- add corresponding value to new fields
UPDATE Students
SET status_id = 
        (SELECT statuses.id FROM statuses
        WHERE statuses.name = students.status);

UPDATE Students
SET project_id = 
        (SELECT projects.id FROM projects
        WHERE projects.name = students.project);

UPDATE Students
SET intake_id = 
        (SELECT intakes.id FROM intakes
        WHERE intakes.name = students.intake);

UPDATE Students
SET pre_internship_internal_eval_level_id =
        (SELECT Internal_eval_levels.id FROM Internal_eval_levels
        WHERE SUBSTR(
                students.pre_internship_summary_recommendation_internal, 
                INSTR(students.pre_internship_summary_recommendation_internal, '-') + 2
                ) 
        = Internal_eval_levels.name);

