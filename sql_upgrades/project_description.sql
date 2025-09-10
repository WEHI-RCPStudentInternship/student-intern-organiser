CREATE TABLE Job_Description_Word_Count (
    about_org_word_limit INTEGER DEFAULT 70,
    position_desc_word_min INTEGER DEFAULT 400,
    position_desc_word_max INTEGER DEFAULT 500,
    skills_word_min INTEGER DEFAULT 50,
    skills_word_max INTEGER DEFAULT 70
);

-- Add all required columns for project job description editing and word limits
ALTER TABLE Projects ADD COLUMN skill_requirements TEXT;
ALTER TABLE Projects ADD COLUMN about_organisation TEXT;
ALTER TABLE Projects ADD COLUMN position_title TEXT;
ALTER TABLE Projects ADD COLUMN position_description TEXT;
ALTER TABLE Projects ADD COLUMN about_org_last_edit_date DATE;
ALTER TABLE Projects ADD COLUMN position_desc_last_edit_date DATE;
ALTER TABLE Projects ADD COLUMN skills_last_edit_date DATE;
