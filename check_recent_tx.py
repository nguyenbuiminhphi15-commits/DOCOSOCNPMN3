import sys
sys.path.append('c:\\Users\\HOANG PC\\Source\\Repos\\Hutech_SecureQR')
from models.database_model import DatabaseModel
db = DatabaseModel()
conn = db.get_connection()
c = conn.cursor()
c.execute("SELECT TOP 5 tx_id, qr_id, created_at FROM Transactions_Ledger ORDER BY created_at DESC")
rows = c.fetchall()
print("Top 5 transactions in DB:")
for r in rows:
    print(r)
