-- Add fields for editable word limits and edit dates for position description and skills
ALTER TABLE Projects ADD COLUMN position_desc_word_min INTEGER DEFAULT 400;
ALTER TABLE Projects ADD COLUMN position_desc_word_max INTEGER DEFAULT 500;
ALTER TABLE Projects ADD COLUMN position_desc_last_edit_date DATE;
ALTER TABLE Projects ADD COLUMN skills_word_min INTEGER DEFAULT 50;
ALTER TABLE Projects ADD COLUMN skills_last_edit_date DATE;
