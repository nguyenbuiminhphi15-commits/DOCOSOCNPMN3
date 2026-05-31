import pyodbc
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=LAPTOP-NPGB1T0P;DATABASE=Hutech_SecureQR;Trusted_Connection=yes;')
cursor = conn.cursor()
try:
    cursor.execute("ALTER TABLE Store_Orders ADD customer_name NVARCHAR(255), customer_phone VARCHAR(20), customer_address NVARCHAR(MAX)")
    conn.commit()
    print("Added customer fields successfully")
except Exception as e:
    print(f"Error: {e}")
