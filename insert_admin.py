import pyodbc

conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=LAPTOP-NPGB1T0P;DATABASE=Hutech_SecureQR;Trusted_Connection=yes;')
cursor = conn.cursor()

# Check if user already exists
cursor.execute("SELECT username FROM Users WHERE username = 'phi'")
if cursor.fetchone():
    print("User 'phi' already exists.")
else:
    try:
        sql = """
        INSERT INTO Users (username, password_hash, bank_account, bank_code, created_at, full_name, role, status, short_name)
        VALUES (?, ?, ?, ?, GETDATE(), ?, ?, ?, ?)
        """
        params = (
            'phi', 
            '$2b$12$06wzh20wt84RsB7yX4o58uLoLc.iBE4LqVkneZrsilklwrMd0eHdC', 
            '96247HOATHUI', 
            'BIDV', 
            'Phi', 
            'ADMIN', 
            'ACTIVE', 
            None
        )
        
        cursor.execute(sql, params)
        conn.commit()
        print("Successfully inserted admin user 'phi' into Users table.")
    except Exception as e:
        print(f"Error inserting user: {e}")

conn.close()
