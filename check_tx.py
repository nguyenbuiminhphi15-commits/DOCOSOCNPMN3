import sys
sys.path.append('c:\\Users\\HOANG PC\\Source\\Repos\\Hutech_SecureQR')
from models.database_model import DatabaseModel
db = DatabaseModel()
conn = db.get_connection()
c = conn.cursor()
c.execute("SELECT U.user_id, TL.tx_id, TL.created_at, U.bank_account FROM Transactions_Ledger TL JOIN QR_Links QL ON TL.qr_id = QL.qr_id JOIN Users U ON QL.user_id = U.user_id")
print("All transactions:", c.fetchall())
