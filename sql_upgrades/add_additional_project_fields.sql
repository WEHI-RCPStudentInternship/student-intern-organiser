-- Add additional description fields to Projects table
ALTER TABLE Projects ADD COLUMN duties_placement TEXT;
ALTER TABLE Projects ADD COLUMN skills_prerequisites TEXT; 
ALTER TABLE Projects ADD COLUMN benefits_students TEXT;
ALTER TABLE Projects ADD COLUMN about_organisation TEXT;
ALTER TABLE Projects ADD COLUMN position_title TEXT;
ALTER TABLE Projects ADD COLUMN position_description TEXT;
ALTER TABLE Projects ADD COLUMN key_skills_development TEXT;
