import sys
import uuid
import datetime
import random
sys.path.append('c:\\Users\\HOANG PC\\Source\\Repos\\Hutech_SecureQR')
from models.database_model import DatabaseModel

db = DatabaseModel()
conn = db.get_connection()
if not conn:
    print("Failed to connect to database")
    sys.exit(1)

cursor = conn.cursor()

# Get the first user
cursor.execute("SELECT TOP 1 user_id FROM Users ORDER BY user_id ASC")
user_row = cursor.fetchone()
if not user_row:
    print("No users found.")
    sys.exit(1)

user_id = user_row[0]

# First, create some QR Links for this user to attach transactions to
qr_ids = []
for i in range(8):
    qr_id = "TEST-" + str(uuid.uuid4())[:8].upper()
    amount = random.choice([50000, 150000, -30000, 200000, -50000, 1000000, -200000, 300000])
    desc = "Thu hộ" if amount > 0 else "Hoàn tiền / Chuyển khoản"
    cursor.execute("""
        INSERT INTO QR_Links (qr_id, user_id, expected_amount, description, hmac_signature, status, created_at)
        VALUES (?, ?, ?, ?, 'mock_hmac', 'ACTIVE', GETDATE())
    """, (qr_id, user_id, amount, f"{desc} DH{random.randint(1000, 9999)}"))
    qr_ids.append((qr_id, amount))

# Then insert Transactions
for i, (qr_id, amount) in enumerate(qr_ids):
    tx_id = str(uuid.uuid4())
    block_hash = f'0000{str(uuid.uuid4()).replace("-", "")}'
    # Giả lập thời gian từ vài ngày trước đến hôm nay
    cursor.execute("""
        INSERT INTO Transactions_Ledger (tx_id, qr_id, actual_amount, payer_ip, ai_risk_score, status, block_hash, created_at)
        VALUES (?, ?, ?, '127.0.0.1', 0, 'SUCCESS', ?, DATEADD(hour, -?, GETDATE()))
    """, (tx_id, qr_id, amount, block_hash, i * 12))

conn.commit()
print(f"✅ Đã tạo thành công {len(qr_ids)} giao dịch mẫu (+ Tiền vào, - Tiền ra) vào database.")
conn.close()
