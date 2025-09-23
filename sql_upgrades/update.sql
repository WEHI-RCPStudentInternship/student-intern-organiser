-- Add these sql queries for new database with new attributes

ALTER TABLE Students
ADD COLUMN remote_internship TEXT;

ALTER TABLE Students
ADD COLUMN code_of_conduct TEXT;

ALTER TABLE Students
ADD COLUMN facilitator_follower TEXT;

ALTER TABLE Students
ADD COLUMN listener_or_talker TEXT;

ALTER TABLE Students
ADD COLUMN thinker_brainstormer TEXT;

ALTER TABLE Students
ADD COLUMN why_applied TEXT;

ALTER TABLE Students
ADD COLUMN projects_recommended TEXT;
