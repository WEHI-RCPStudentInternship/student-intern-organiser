import sqlite3

# Connect to the database
conn = sqlite3.connect('student_intern_data/student_intern_data.db')
cursor = conn.cursor()

print("Running migration: add_foreign_key_columns.sql")
print("=" * 80)

# Read and execute the migration script
with open('sql_upgrades/add_foreign_key_columns.sql', 'r') as f:
    sql_script = f.read()

try:
    cursor.executescript(sql_script)
    conn.commit()
    print("✓ Migration completed successfully!")
    
    # Verify the migration
    print("\nVerifying migration...")
    
    null_status_ids = cursor.execute("SELECT COUNT(*) FROM Students WHERE status_id IS NULL").fetchone()[0]
    null_intake_ids = cursor.execute("SELECT COUNT(*) FROM Students WHERE intake_id IS NULL").fetchone()[0]
    
    print(f"  Students with NULL status_id: {null_status_ids}")
    print(f"  Students with NULL intake_id: {null_intake_ids}")
    
    if null_status_ids == 0 and null_intake_ids == 0:
        print("\n✓ All students have valid status_id and intake_id values")
    else:
        print("\n⚠ Warning - some students have NULL values")
        
except Exception as e:
    print(f"✗ Error during migration: {e}")
    conn.rollback()
finally:
    conn.close()
