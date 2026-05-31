# File: utils/crypto_utils.py
import hmac
import hashlib
import json

class SecurityEngine:
    def __init__(self):
        # ĐÂY LÀ CHÌA KHÓA BÍ MẬT CỦA HỆ THỐNG (Tuyệt đối không để lộ)
        # Thực tế người ta sẽ giấu nó vào file .env, ở đồ án ta tạm để đây
        self.secret_key = b"Hutech_CyberSecurity_Secret_Key_2026"

    def generate_hmac_signature(self, account_number, amount, qr_id):
        """
        Hàm tạo chữ ký số cho mã QR dựa trên dữ liệu giao dịch
        """
        # 1. Gom các dữ liệu quan trọng lại thành một chuỗi duy nhất
        raw_data = f"{account_number}|{amount}|{qr_id}"
        
        # 2. Dùng thuật toán HMAC-SHA256 để băm chuỗi này cùng với Secret Key
        signature = hmac.new(
            self.secret_key, 
            raw_data.encode('utf-8'), 
            hashlib.sha256
        ).hexdigest()
        
        return signature

    def verify_qr_tampering(self, account_number, amount, qr_id, provided_signature):
        """
        Hàm kiểm tra xem mã QR có bị kẻ gian chỉnh sửa hay không
        """
        # Tạo lại chữ ký từ dữ liệu người dùng quét được
        expected_signature = self.generate_hmac_signature(account_number, amount, qr_id)
        
        # So sánh (dùng compare_digest để chống lỗi Timing Attack)
        return hmac.compare_digest(expected_signature, provided_signature)


        # ... (Các code cũ giữ nguyên) ...

    def generate_block_hash(self, tx_id, qr_id, actual_amount, payer_ip, ai_score, status):
        """
        Đóng gói giao dịch thành một Block không thể chỉnh sửa (SHA-256)
        """
        # 1. Gom toàn bộ thông tin giao dịch thành một khối dữ liệu
        block_data = f"{tx_id}|{qr_id}|{actual_amount}|{payer_ip}|{ai_score}|{status}"
        
        # 2. Trộn thêm Secret Key vào để hacker không thể tự tạo mã băm khớp được
        secure_block_data = block_data + self.secret_key.decode('utf-8')
        
        # 3. Băm nát dữ liệu bằng thuật toán SHA-256
        block_hash = hashlib.sha256(secure_block_data.encode('utf-8')).hexdigest()
        
        return block_hash

# Code để bạn test nhanh (sẽ tự chạy nếu bạn nhấn Play file này)
if __name__ == "__main__":
    engine = SecurityEngine()
    
    # Giả lập: Tạo chữ ký cho giao dịch 500k của tài khoản admin
    chu_ky = engine.generate_hmac_signature("96247HOATHUI", 500000, "QR_001")
    print(f"🔒 Chữ ký số an toàn sinh ra:\n{chu_ky}")
    
    # Giả lập: Hacker sửa số tiền thành 5k
    print("\n🕵️ AI đang kiểm tra tính toàn vẹn...")
    is_valid = engine.verify_qr_tampering("96247HOATHUI", 5000, "QR_001", chu_ky)
    if is_valid:
        print("✅ Hợp lệ!")
    else:
        print("🚨 BÁO ĐỘNG: Mã QR đã bị thay đổi dữ liệu!")