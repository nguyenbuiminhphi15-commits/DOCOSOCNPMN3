import hashlib
import json
import time
import os

class Blockchain:
    def __init__(self):
        self.chain = []
        self.ledger_file = os.path.join(os.path.dirname(__file__), '..', 'ledger.json')
        
        # Thử nạp sổ cái từ file (nếu server bị khởi động lại)
        if os.path.exists(self.ledger_file):
            try:
                with open(self.ledger_file, 'r', encoding='utf-8') as f:
                    self.chain = json.load(f)
            except Exception:
                self.chain = []

        # Nếu sổ cái trống, tạo khối khởi đầu (Genesis Block)
        if len(self.chain) == 0:
            self.create_block(previous_hash='0', data="Genesis Block")

    def save_ledger(self):
        """Lưu trữ chuỗi khối xuống ổ cứng để không bị mất khi tắt server"""
        with open(self.ledger_file, 'w', encoding='utf-8') as f:
            json.dump(self.chain, f, ensure_ascii=False, indent=4)

    def create_block(self, data, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'data': data,
            'previous_hash': previous_hash,
            'hash': self.calculate_hash(data, previous_hash)
        }
        self.chain.append(block)
        self.save_ledger() # Gọi hàm lưu sau mỗi lần có block mới
        return block

    def calculate_hash(self, data, previous_hash):
        encoded_block = json.dumps({'data': data, 'previous_hash': previous_hash}, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def get_last_block(self):
        return self.chain[-1]