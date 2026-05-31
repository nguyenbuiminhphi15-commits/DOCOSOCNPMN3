import pyodbc
from models.database_model import DatabaseModel

db = DatabaseModel()
conn = db.get_connection()
if conn:
    cursor = conn.cursor()
    try:
        cursor.execute("""
        IF COL_LENGTH('Users', 'full_name') IS NULL
        BEGIN
            ALTER TABLE Users ADD full_name NVARCHAR(100)
        END
        """)
        
        cursor.execute("""
        IF COL_LENGTH('Users', 'role') IS NULL
        BEGIN
            ALTER TABLE Users ADD role VARCHAR(20) DEFAULT 'MERCHANT'
            EXEC('UPDATE Users SET role = ''MERCHANT'' WHERE role IS NULL')
        END
        """)
        
        cursor.execute("UPDATE Users SET role = 'ADMIN' WHERE username = 'qskaitomz@gmail.com'")
        
        conn.commit()
        print('Database schema updated successfully!')
    except Exception as e:
        print(f'Error: {e}')
    finally:
        conn.close()
