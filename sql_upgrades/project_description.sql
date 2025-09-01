
-- Add maximum word limit field for skills
ALTER TABLE Projects ADD COLUMN skills_word_max INTEGER DEFAULT 70;

-- Add description fields to Projects table
ALTER TABLE Projects ADD COLUMN organization_description TEXT;
ALTER TABLE Projects ADD COLUMN project_description TEXT;
ALTER TABLE Projects ADD COLUMN skill_requirements TEXT;

-- Add fields for editable word limits and edit dates
ALTER TABLE Projects ADD COLUMN about_org_word_limit INTEGER DEFAULT 70;
ALTER TABLE Projects ADD COLUMN about_org_last_edit_date DATE;

-- Add fields for editable word limits and edit dates for position description and skills
ALTER TABLE Projects ADD COLUMN position_desc_word_min INTEGER DEFAULT 400;
ALTER TABLE Projects ADD COLUMN position_desc_word_max INTEGER DEFAULT 500;
ALTER TABLE Projects ADD COLUMN position_desc_last_edit_date DATE;
ALTER TABLE Projects ADD COLUMN skills_word_min INTEGER DEFAULT 50;
ALTER TABLE Projects ADD COLUMN skills_last_edit_date DATE;

-- Add additional description fields to Projects table
ALTER TABLE Projects ADD COLUMN duties_placement TEXT;
ALTER TABLE Projects ADD COLUMN skills_prerequisites TEXT; 
ALTER TABLE Projects ADD COLUMN benefits_students TEXT;
ALTER TABLE Projects ADD COLUMN about_organisation TEXT;
ALTER TABLE Projects ADD COLUMN position_title TEXT;
ALTER TABLE Projects ADD COLUMN position_description TEXT;
ALTER TABLE Projects ADD COLUMN key_skills_development TEXT;
