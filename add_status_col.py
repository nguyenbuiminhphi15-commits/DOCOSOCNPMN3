import pyodbc
from models.database_model import DatabaseModel

db = DatabaseModel()
conn = db.get_connection()
if conn:
    cursor = conn.cursor()
    try:
        cursor.execute("""
        IF COL_LENGTH('Users', 'status') IS NULL
        BEGIN
            ALTER TABLE Users ADD status VARCHAR(20) DEFAULT 'ACTIVE'
            EXEC('UPDATE Users SET status = ''ACTIVE'' WHERE status IS NULL')
        END
        """)
        conn.commit()
        print('Status column added successfully!')
    except Exception as e:
        print(f'Error: {e}')
    finally:
        conn.close()
