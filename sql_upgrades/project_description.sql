CREATE TABLE Job_Description_Word_Count (
    about_org_word_min INTEGER,
    about_org_word_max INTEGER,
    position_desc_word_min INTEGER,
    position_desc_word_max INTEGER,
    skills_word_min INTEGER,
    skills_word_max INTEGER
);

-- Add new columns to Projects table
ALTER TABLE Projects ADD COLUMN skill_requirements TEXT;
ALTER TABLE Projects ADD COLUMN about_organisation TEXT;
ALTER TABLE Projects ADD COLUMN position_title TEXT;
ALTER TABLE Projects ADD COLUMN position_description TEXT;

INSERT INTO Job_Description_Word_Count (
    about_org_word_min, about_org_word_max,
    position_desc_word_min, position_desc_word_max,
    skills_word_min, skills_word_max
) VALUES (1, 70, 400, 500, 50, 70);