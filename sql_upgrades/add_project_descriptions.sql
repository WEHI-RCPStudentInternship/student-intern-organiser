-- Add description fields to Projects table
ALTER TABLE Projects ADD COLUMN organization_description TEXT;
ALTER TABLE Projects ADD COLUMN project_description TEXT;
ALTER TABLE Projects ADD COLUMN skill_requirements TEXT;
