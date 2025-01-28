-- Upgrade script for student_intern_data.db from Semester 1, 2024 to Semester 2, 2024

-- To upgrade your local database:
-- 1. Make sure you have a backup of your current database.
-- 2. Open your SQL client and connect to your local instance of student_intern_data.db.
-- 3. Run the `upgrade_database.sql` script provided.
-- 4. Verify the schema changes by checking for the new changes manually.
-- 5. Write the updates in the database_change_history.sql file

-- Create the schema file for the database using the following command:
-- sqlite3 student_intern_data_public/student_intern_data.db .schema > schema_public.sql

--To run the following changes, follow these steps:
-- 1. Navigate to the directory containing your database
-- 2. Make sure SQLite is installed (check by typing sqlite3)
-- 3. Run the command: sqlite3 student_intern_data.db
-- 4. Execute the sql script using the .read command: .read upgrade_database.sql
-- 5. Verify the changes: PRAGMA table_info(Students);
-- 6. Exit SQLite: .exit
-- 7. Comment out the query corresponding to the change you made

-- Date: 2 September, 2024
-- This script upgrades the database schema to include new fields in the Students and Intakes tables.

-- Adding new columns to the Students table
ALTER TABLE Students ADD COLUMN remote_internship TEXT; -- Added to capture if the internship is remote
ALTER TABLE Students ADD COLUMN code_of_conduct TEXT; -- Added to store information about code of conduct agreement
ALTER TABLE Students ADD COLUMN facilitator_follower TEXT; -- Added to indicate if the student is a facilitator or follower
ALTER TABLE Students ADD COLUMN listener_or_talker TEXT; -- Added to categorise the student as a listener or talker
ALTER TABLE Students ADD COLUMN thinker_brainstormer TEXT; -- Added to identify if the student is a thinker or brainstormer
ALTER TABLE Students ADD COLUMN why_applied TEXT; -- Added to store reasons why the student applied
ALTER TABLE Students ADD COLUMN projects_recommended TEXT; -- Added to capture projects recommended to the student

-- Adding new columns to the Intakes table
ALTER TABLE Intakes ADD COLUMN science_start_date DATE; -- Added to track the start date for science intakes
ALTER TABLE Intakes ADD COLUMN engit_start_date DATE; -- Added to track the start date for engineering intakes

-- No changes needed for the Statuses and Projects tables as per the provided schemas.