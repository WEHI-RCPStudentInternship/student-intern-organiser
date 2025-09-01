-- 12th January 2025
alter table students add column redcap_id text;

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

-- Create Email Schedule table for storing intake email dates and content
CREATE TABLE IF NOT EXISTS EmailSchedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    intake_id INTEGER,
    week_number TEXT,
    week_offset_days INTEGER,
    date_for_interns DATE,
    subject TEXT,
    body TEXT,
    created_date DATE DEFAULT CURRENT_DATE,
    last_modified DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (intake_id) REFERENCES Intakes(id)
);

-- Insert default email schedule data with proper week offsets
-- Week 0 (1 week before): -7 days (Monday before start)
-- Week 1 (First week): 0 days (Monday of start week)
-- Week 2 (Second week): 7 days (Monday of week 2)
-- Week 4 (Fourth week): 21 days (Monday of week 4)
-- Week 10 (Tenth week): 63 days (Monday of week 10 = 7 x 9 days after start)
-- Week 13 (End): 84 days (Monday of week 13 = 7 x 12 days after start)
INSERT INTO EmailSchedule (id, intake_id, week_number, week_offset_days, subject, body) VALUES
(1, 1, '0 - 1 week before', -7, '1 week before WEHI internship', 'Hi All, This is your email to start your internship preparation...'),
(2, 1, '1 - First week', 0, 'First week of WEHI internship', 'Hi All, Welcome to your first week of internship...'),
(3, 1, '2 - Second week', 7, 'Second week of WEHI internship', 'Hi All, This is your second week of internship...'),
(4, 1, '4 - Fourth week', 21, 'Fourth week of WEHI internship', 'Hi All, This is your email to start week 4 of your internship...'),
(5, 1, '10 - Tenth week', 63, 'Tenth week of WEHI internship', 'Hi All, This is your email to start week 10 of your internship...'),
(6, 1, '13 - End of internship', 84, 'End of WEHI internship', 'Hi All, I would like to thank you all for being a part of this intake...');

-- (Other .sql files were empty and are not included)
