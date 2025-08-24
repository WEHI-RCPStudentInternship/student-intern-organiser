-- Add maximum word limit field for skills
ALTER TABLE Projects ADD COLUMN skills_word_max INTEGER DEFAULT 70;
