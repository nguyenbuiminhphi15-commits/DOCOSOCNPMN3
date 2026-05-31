import sys
import requests
sys.path.append('c:\\Users\\HOANG PC\\Source\\Repos\\Hutech_SecureQR')
from models.database_model import DatabaseModel
import uuid

db = DatabaseModel()
conn = db.get_connection()
c = conn.cursor()

# Get a user
c.execute("SELECT TOP 1 user_id FROM Users")
user_id = c.fetchone()[0]

# Create a fresh QR_Links
qr_id = "TEST-" + str(uuid.uuid4())[:8].upper()
c.execute("INSERT INTO QR_Links (qr_id, user_id, expected_amount, status, hmac_signature) VALUES (?, ?, 50000, 'ACTIVE', 'mock_hmac')", (qr_id, user_id))
conn.commit()

print(f"Created QR: {qr_id}")

# Fire Webhook
res = requests.post('http://127.0.0.1:5000/api/webhook/sepay', json={'transferAmount': 50000, 'transactionContent': f'{qr_id} Thanh toan'})
print("Webhook response:", res.status_code, res.json())

# Check if it was inserted into Transactions_Ledger
c.execute("SELECT * FROM Transactions_Ledger WHERE qr_id = ?", (qr_id,))
tx = c.fetchone()
if tx:
    print("SUCCESS: Transaction found in Ledger!", tx.tx_id)
else:
    print("FAILED: Transaction NOT found in Ledger.")
