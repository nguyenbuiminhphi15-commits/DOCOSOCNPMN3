# File: controllers/qr_controller.py
from flask import Blueprint, request, jsonify, session
from models.database_model import DatabaseModel
import random
import string
import uuid
import urllib.parse
import requests
import json
from utils.crypto_utils import SecurityEngine
from utils.blockchain_engine import BlockchainEngine

qr_bp = Blueprint('qr', __name__)
db = DatabaseModel()
security_engine = SecurityEngine()

# HÀM MẮT THẦN: CHỦ ĐỘNG QUÉT GIAO DỊCH TRÊN SEPAY (ĐÃ NÂNG CẤP ĐỌC CHỮ)
def fetch_transaction_from_sepay(ma_don_hang, token_id=None):
    # 1. Kết nối CSDL để lôi Token ra
    conn = db.get_connection()
    sepay_token = ""
    if conn:
        try:
            cursor = conn.cursor()
            if token_id:
                cursor.execute("SELECT token_string FROM Sepay_Tokens WHERE id = ?", (token_id,))
                row = cursor.fetchone()
                if row:
                    sepay_token = row[0]
            else:
                cursor.execute("SELECT TOP 1 token_string FROM Sepay_Tokens WHERE is_active = 1 ORDER BY created_at DESC")
                row = cursor.fetchone()
                if row:
                    sepay_token = row[0]
        except Exception as e:
            print("Lỗi lấy Token từ DB:", e)
        finally:
            conn.close()

    # Nếu Admin chưa nhập Token thì ngưng luôn, không gọi SePay
    if not sepay_token:
        print("⚠️ Cảnh báo: Hệ thống chưa được cấu hình API Token!")
        return None

    # 2. Bắt đầu gọi API SePay với Token vừa lấy được
    url = "https://my.sepay.vn/userapi/transactions/list"
    headers = {
        "Authorization": f"Bearer {sepay_token}",
        "Content-Type": "application/json"
    }
    # Lấy 20 giao dịch gần nhất
    params = {
        "limit": 20
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            transactions = data.get('transactions', [])
            
            # DUYỆT QUA TỪNG GIAO DỊCH ĐỂ SOI NỘI DUNG
            for txn in transactions:
                # Lấy nội dung chuyển khoản ép thành chữ in hoa
                content = str(txn.get('transaction_content', '')).upper()
                
                # Tạo một phiên bản mã đơn hàng không có dấu gạch dưới
                ma_ko_gach = ma_don_hang.upper().replace('_', '')
                
                # NẾU TÌM THẤY MÃ GỐC HOẶC MÃ KHÔNG GẠCH -> CHỐT!
                if ma_don_hang.upper() in content or ma_ko_gach in content:
                    actual_amount = float(txn.get('amount_in', 0))
                    print(f"🕵️‍♂️ [MẮT THẦN API] TÌM THẤY! Khách đã chuyển {actual_amount}đ cho đơn {ma_don_hang}")
                    return actual_amount, content
                    
    except Exception as e:
        print(f"Lỗi gọi API SePay: {e}")
        
    return None, None # Không tìm thấy thì trả về None, bắt Web tiếp tục chờ!

# ==========================================================
# 1. API KHỞI TẠO GIAO DỊCH (TẠO MÃ ĐƠN HÀNG DUY NHẤT)
# ==========================================================
import hmac
import hashlib

@qr_bp.route('/api/create-transaction', methods=['POST'])
def create_transaction():
    data = request.json
    
    # 1. Sinh mã giao dịch ngẫu nhiên (chỉ dùng SỐ để tương thích 100% các App Ngân hàng)
    random_str = ''.join(random.choices(string.digits, k=6))
    unique_qr_id = f"HUTECH{random_str}"
    
    # 2. Ghép nội dung người dùng nhập với mã độc nhất
    user_desc = data.get('description', '').strip()
    if user_desc:
        final_desc = f"{user_desc} {unique_qr_id}"
    else:
        final_desc = unique_qr_id

    # 3. Lấy số tiền từ Frontend gửi xuống (Nếu không có thì mặc định là 0)
    amount = data.get('amount', 0)
    if not amount or amount == '':
        amount = 0

    token_id = data.get('token_id')
    if not token_id:
        return jsonify({"success": False, "message": "Vui lòng chọn Cửa hàng / API Key"}), 400

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "message": "Phiên đăng nhập hết hạn"}), 401

    # ==========================================
    # BỔ SUNG: TẠO CHỮ KÝ HMAC-SHA256 BẢO MẬT
    # ==========================================
    secret_key = b"HUTECH_SECURE_SECRET_KEY_2026" # Khóa bí mật của Server
    # Băm kết hợp mã đơn hàng và số tiền
    data_to_sign = f"{final_desc}|{amount}".encode('utf-8')
    signature = hmac.new(secret_key, data_to_sign, hashlib.sha256).hexdigest()

    conn = db.get_connection()
    if not conn:
        return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

    try:
        cursor = conn.cursor()
        
        # 4. CẬP NHẬT LỆNH SQL: Thêm cột token_id và user_id vào lệnh INSERT
        sql = "INSERT INTO QR_Links (qr_id, user_id, expected_amount, hmac_signature, status, token_id) VALUES (?, ?, ?, ?, 'ACTIVE', ?)"
        cursor.execute(sql, (final_desc, user_id, amount, signature, token_id))
        conn.commit()

        # Trả mã Nội dung về cho Frontend tạo link
        return jsonify({"success": True, "qr_id": final_desc}), 200
        
    except Exception as e:
        print(f"❌ Lỗi tạo giao dịch QR: {e}")
        return jsonify({"success": False, "message": "Lỗi hệ thống"}), 500
    finally:
        conn.close()

# ==========================================================
# 2. API RADAR - KIỂM TRA TRẠNG THÁI TIỀN VỀ
# ==========================================================
@qr_bp.route('/api/check-payment-status', methods=['GET'])
def check_payment_status():
    qr_id = request.args.get('qr_id') 
    
    conn = db.get_connection()
    if not conn:
        return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500
        
    try:
        cursor = conn.cursor()
        
        # 1. ƯU TIÊN KIỂM TRA DATABASE
        cursor.execute("SELECT status, token_id FROM QR_Links WHERE qr_id = ?", (qr_id,))
        row = cursor.fetchone()
        
        if not row:
            return jsonify({"success": False, "message": "Không tìm thấy mã QR"}), 404
            
        if row[0] == 'PAID':
            return jsonify({"success": True, "status": "PAID"}), 200
            
        token_id = row[1]
            
        # 2. KÍCH HOẠT MẮT THẦN DÙNG TOKEN
        actual_amount, transfer_content = fetch_transaction_from_sepay(qr_id, token_id)
        
        if actual_amount is not None:
            # 1. Gạch nợ trạng thái bảng QR với chốt chặn tranh chấp
            cursor.execute("UPDATE QR_Links SET status = 'PAID' WHERE qr_id = ? AND status = 'ACTIVE'", (qr_id,))
            affected_rows = cursor.rowcount
            
            if affected_rows > 0:
                print(f"✅ Đã giành được quyền đóng khối cho đơn {qr_id} (Polling)")
                # 2. LƯU VÀO BLOCKCHAIN
                b_engine = BlockchainEngine(db)
                
                # Đóng gói thông tin giao dịch thành JSON để nhét vào Block
                tx_data = json.dumps({
                    "qr_id": qr_id,
                    "amount": actual_amount,
                    "type": "SEPAY_TRANSFER"
                })
                
                # Kích hoạt máy đào!
                block_hash = b_engine.mine_and_save_block(tx_data)
                
                # 3. LƯU VÀO SỔ CÁI GIAO DỊCH (TRANSACTIONS LEDGER)
                import uuid
                tx_id = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO Transactions_Ledger (tx_id, qr_id, actual_amount, payer_ip, ai_risk_score, status, block_hash, transfer_content, created_at)
                    VALUES (?, ?, ?, ?, 0, 'SUCCESS', ?, ?, GETDATE())
                """, (tx_id, qr_id, actual_amount, request.remote_addr or '127.0.0.1', block_hash, transfer_content))
                
                conn.commit()
            else:
                print(f"⚠️ Bỏ qua đóng khối cho đơn {qr_id} vì luồng khác đã xử lý rồi.")
                conn.rollback()
                
            return jsonify({"success": True, "status": "PAID"}), 200

        return jsonify({"success": True, "status": "ACTIVE"}), 200
        
    except Exception as e:
        print(f"❌ Lỗi kiểm tra thanh toán: {e}")
        return jsonify({"success": False, "message": "Lỗi SQL"}), 500
    finally:
        if conn:
            conn.close()

# ==========================================================
# 3. API ADMIN CẬP NHẬT TOKEN
# ==========================================================
@qr_bp.route('/api/admin/update-token', methods=['POST'])
def update_token():
    data = request.json
    action = data.get('action')
    
    conn = db.get_connection()
    if not conn:
        return jsonify({"success": False, "message": "Lỗi CSDL"}), 500
        
    try:
        cursor = conn.cursor()
        
        if action == 'delete':
            token_id = data.get('id')
            cursor.execute("DELETE FROM Sepay_Tokens WHERE id = ?", (token_id,))
            conn.commit()
            return jsonify({"success": True, "message": "Đã xóa API thành công!"}), 200
            
        elif action == 'edit':
            token_id = data.get('id')
            new_name = data.get('name').strip()
            new_status = 1 if data.get('status') == 'ACTIVE' else 0
            cursor.execute("UPDATE Sepay_Tokens SET token_name = ?, is_active = ? WHERE id = ?", (new_name, new_status, token_id))
            conn.commit()
            return jsonify({"success": True, "message": "Cập nhật API thành công!"}), 200

        else:
            new_token = data.get('api_token', '').strip()
            new_name = data.get('name', 'thanh toán cửa hàng 1').strip()
            new_status = 1 if data.get('status', 'ACTIVE').strip() == 'ACTIVE' else 0
            
            if not new_token:
                return jsonify({"success": False, "message": "Vui lòng nhập Token"}), 400
                
            # ==========================================
            # BƯỚC KIỂM TRA TRÙNG LẶP (CHỐNG DUPLICATE)
            # ==========================================
            cursor.execute("SELECT id FROM Sepay_Tokens WHERE token_string = ?", (new_token,))
            existing_token = cursor.fetchone()
            
            if existing_token:
                return jsonify({
                    "success": False, 
                    "message": "⚠️ Bíp bíp! Mã API Token này đã tồn tại trong hệ thống rồi."
                }), 400
                
            cursor.execute("INSERT INTO Sepay_Tokens (token_name, token_string, is_active) VALUES (?, ?, ?)", (new_name, new_token, new_status))
            conn.commit()
            return jsonify({"success": True, "message": "Lưu Token thành công!"}), 200
    except Exception as e:
        print(f"Lỗi cập nhật Token: {e}")
        return jsonify({"success": False, "message": "Lỗi hệ thống"}), 500
    finally:
        conn.close()
