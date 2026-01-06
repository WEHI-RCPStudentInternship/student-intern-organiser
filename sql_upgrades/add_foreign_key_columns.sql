-- Migration to add foreign key columns for status_id and intake_id

--  Add the new ID columns
ALTER TABLE Students ADD COLUMN status_id INTEGER;
ALTER TABLE Students ADD COLUMN intake_id INTEGER;


-- Match status text to Statuses.name
UPDATE Students
SET status_id = (
    SELECT id FROM Statuses 
    WHERE Statuses.name = Students.status
);

-- awra intake_id via Intakes.name
UPDATE Students
SET intake_id = (
    SELECT id FROM Intakes 
    WHERE Intakes.name = Students.intake
);


