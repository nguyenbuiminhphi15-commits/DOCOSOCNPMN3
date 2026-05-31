import sys
sys.path.append('c:\\Users\\HOANG PC\\Source\\Repos\\Hutech_SecureQR')
from models.database_model import DatabaseModel
db = DatabaseModel()
conn = db.get_connection()
cursor = conn.cursor()
try:
    query = """
        SELECT 
            TL.tx_id, 
            TL.created_at, 
            U.bank_account, 
            U.bank_code,
            QL.account_no, 
            TL.actual_amount, 
            QL.description,
            TL.block_hash,
            TL.status
        FROM Transactions_Ledger TL
        JOIN QR_Links QL ON TL.qr_id = QL.qr_id
        JOIN Users U ON QL.user_id = U.user_id
        WHERE U.user_id = 1
        ORDER BY TL.created_at DESC
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    print("Number of transactions fetched:", len(rows))
    for r in rows:
        print(r)
except Exception as e:
    print("ERROR:", e)
