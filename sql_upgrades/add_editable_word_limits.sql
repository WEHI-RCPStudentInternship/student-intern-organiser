-- Add fields for editable word limits and edit dates
ALTER TABLE Projects ADD COLUMN about_org_word_limit INTEGER DEFAULT 70;
ALTER TABLE Projects ADD COLUMN about_org_last_edit_date DATE;
