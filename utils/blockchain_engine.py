import hashlib
import json
from datetime import datetime

class BlockchainEngine:
    def __init__(self, db_model):
        self.db = db_model
        self.difficulty = 4  # Độ khó: Hash phải bắt đầu bằng 4 số '0' (VD: 0000abcd...)
        self._initialize_genesis_block()

    def _initialize_genesis_block(self):
        """Khởi tạo Khối nguyên thủy (Genesis Block) nếu CSDL chưa có gì"""
        conn = self.db.get_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            cursor.execute("IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Hutech_Blockchain' and xtype='U') RETURN") # Skip if table doesn't exist yet
            cursor.execute("SELECT COUNT(*) FROM Hutech_Blockchain")
            count = cursor.fetchone()[0]
            
            if count == 0:
                print("⚙️ Đang tạo Genesis Block...")
                genesis_data = json.dumps({"message": "HUTECH SECURE GENESIS BLOCK 2026"})
                self.mine_and_save_block(genesis_data, "0" * 64)
        except Exception as e:
            print("Genesis check skipped or error:", e)
        finally:
            conn.close()

    def hash_block(self, block_index, timestamp, data, nonce, previous_hash):
        """Thuật toán băm gom toàn bộ dữ liệu của 1 Khối"""
        block_string = f"{block_index}{timestamp}{data}{nonce}{previous_hash}".encode('utf-8')
        return hashlib.sha256(block_string).hexdigest()

    def mine_and_save_block(self, transactions_data, previous_hash=None):
        """Thuật toán Đào (Proof of Work) và lưu vào SQL"""
        conn = self.db.get_connection()
        if not conn: return False
        
        try:
            cursor = conn.cursor()
            
            # 1. Lấy thông tin Khối cuối cùng
            if previous_hash is None:
                cursor.execute("SELECT TOP 1 block_index, block_hash FROM Hutech_Blockchain ORDER BY block_index DESC")
                last_block = cursor.fetchone()
                if last_block:
                    last_index = last_block[0]
                    previous_hash = last_block[1]
                else:
                    last_index = 0
                    previous_hash = "0" * 64 # Fallback if empty
            else:
                last_index = 0

            new_index = last_index + 1
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            nonce = 0
            
            print(f"⛏️ Đang đào Block #{new_index}...")
            
            # 2. PROOF OF WORK: Chạy vòng lặp tìm Nonce cho đến khi Hash đạt chuẩn
            while True:
                block_hash = self.hash_block(new_index, timestamp, transactions_data, nonce, previous_hash)
                
                # Kiểm tra xem Hash có bắt đầu bằng '0000' không
                if block_hash[:self.difficulty] == "0" * self.difficulty:
                    print(f"💎 Đào thành công! Nonce: {nonce} | Hash: {block_hash}")
                    break
                nonce += 1

            # 3. Đóng gói và cất vào CSDL
            sql = """
                INSERT INTO Hutech_Blockchain 
                (timestamp, transactions_data, nonce, previous_hash, block_hash)
                VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(sql, (timestamp, transactions_data, nonce, previous_hash, block_hash))
            conn.commit()
            return block_hash

        except Exception as e:
            print(f"❌ Lỗi Blockchain: {e}")
            return None
        finally:
            conn.close()

    def verify_chain(self):
        """Chức năng Kiểm toán: Quét toàn bộ CSDL xem có bị Hacker sửa dữ liệu không"""
        conn = self.db.get_connection()
        if not conn: return False
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT block_index, timestamp, transactions_data, nonce, previous_hash, block_hash FROM Hutech_Blockchain ORDER BY block_index ASC")
            blocks = cursor.fetchall()
            
            if len(blocks) == 0:
                print("⚠️ Blockchain trống!")
                return True

            for i in range(1, len(blocks)):
                current = blocks[i]
                previous = blocks[i-1]
                
                # Cấu trúc: [0]index, [1]timestamp, [2]data, [3]nonce, [4]prev_hash, [5]hash
                
                # 1. Kiểm tra Móc xích có khớp không
                if current[4] != previous[5]:
                    print(f"🚨 PHÁT HIỆN GIAN LẬN: Móc xích bị đứt tại Block #{current[0]}!")
                    return False
                    
                # 2. Băm thử lại dữ liệu xem có bị chỉnh sửa ngầm không
                # datetime object to string conversion is tricky, handle correctly based on DB return type
                ts_str = current[1].strftime("%Y-%m-%d %H:%M:%S") if isinstance(current[1], datetime) else str(current[1])[:19]

                recalculated_hash = self.hash_block(current[0], ts_str, current[2], current[3], current[4])
                
                if recalculated_hash != current[5]:
                    print(f"🚨 PHÁT HIỆN GIAN LẬN: Dữ liệu Block #{current[0]} đã bị thay đổi!")
                    return False

            print("✅ HỆ THỐNG AN TOÀN: Toàn bộ Blockchain hợp lệ và nguyên vẹn.")
            return True
            
        finally:
            conn.close()
