import pyodbc
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=LAPTOP-NPGB1T0P;DATABASE=Hutech_SecureQR;Trusted_Connection=yes;')
cursor = conn.cursor()
try:
    cursor.execute("ALTER TABLE Store_Orders ADD details NVARCHAR(MAX)")
    conn.commit()
    print("Added details column successfully")
except Exception as e:
    print(f"Error: {e}")
