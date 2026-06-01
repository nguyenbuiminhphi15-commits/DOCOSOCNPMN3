import pyodbc
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=LAPTOP-NPGB1T0P;DATABASE=Hutech_SecureQR;Trusted_Connection=yes;')
cursor = conn.cursor()
cursor.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Users'")
for row in cursor.fetchall():
    print(f"{row.COLUMN_NAME}: {row.DATA_TYPE}")
