reate backup of original schema - Copy schema.sql to schema_backup_YYYYMMDD.sql with timestamp for safe rollback reference.

Update schema.sql with new foreign key columns - Add status_id INTEGER and intake_id INTEGER columns to schema.sql:2, create FOREIGN KEY constraints referencing schema.sql:47 and schema.sql:51, keep old status TEXT and intake TEXT columns temporarily for migration safety.

Create migration SQL script - Add new file in sql_upgrades/ folder following existing patterns (like update.sql) with: ALTER TABLE to add new columns, UPDATE statements to populate status_id and intake_id from existing TEXT values by joining with lookup tables, validation queries to ensure no data loss.

Update application code queries - Modify app.py (~40 locations) to use status_id/intake_id with JOINs for display names, update INSERT/UPDATE statements (e.g., RedCap import, edit routes), change WHERE clauses from text matching to integer comparisons, modify form handlers to accept IDs from dropdowns (templates already use Statuses table).

Test migration and optionally remove old columns - Run migration script on test database, verify all queries work with new foreign keys, validate data integrity, once confident remove status TEXT and intake TEXT columns from schema.