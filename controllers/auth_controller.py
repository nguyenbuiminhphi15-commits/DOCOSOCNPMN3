from flask import Blueprint, request, jsonify, session
import bcrypt
import re  # Thư viện Regular Expression dùng để quét ký tự đặc biệt và chữ hoa
from models.database_model import DatabaseModel

auth_bp = Blueprint('auth', __name__)
db = DatabaseModel()

# ==========================================================
# 1. API ĐĂNG KÝ (Có quét độ mạnh mật khẩu & check trùng)
# ==========================================================
@auth_bp.route('/api/register', methods=['POST'])
def register_user():
    data = request.json
    email = data.get('email') 
    password = data.get('password')
    first_name = data.get('firstName', '')
    last_name = data.get('lastName', '')
    full_name = f"{last_name} {first_name}".strip().title()
    
    # --- MÀNG LỌC 1: KIỂM TRA ĐỘ MẠNH MẬT KHẨU TRÊN BACKEND ---
    if not password or len(password) < 6:
        return jsonify({"success": False, "message": "Mật khẩu phải có ít nhất 6 ký tự!"}), 400
        
    if not re.search(r'[A-Z]', password):
        return jsonify({"success": False, "message": "Mật khẩu phải chứa ít nhất 1 chữ in HOA!"}), 400
        
    if not re.search(r'[^a-zA-Z0-9]', password):
        return jsonify({"success": False, "message": "Mật khẩu phải chứa ít nhất 1 ký tự đặc biệt (VD: @, #, $, %...)!"}), 400
    # ---------------------------------------------------------

    conn = db.get_connection()
    if not conn:
        return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500
        
    try:
        cursor = conn.cursor()
        print(f"\\n📩 [DEBUG ĐĂNG KÝ] Frontend gửi lên Email: '{email}'")
        
        # --- MÀNG LỌC 2: KIỂM TRA TRÙNG EMAIL ---
        cursor.execute("SELECT user_id, username FROM Users WHERE username = ?", (email,))
        user_row = cursor.fetchone()
        
        if user_row:
            print(f"🚨 [DEBUG ĐĂNG KÝ] Phát hiện trùng lặp với User ID: {user_row[0]}!")
            return jsonify({
                "success": False, 
                "error_type": "email_exists", 
                "message": "Email này đã được đăng ký. Vui lòng dùng email khác!"
            }), 400
            
        # --- BƯỚC 3: BĂM MẬT KHẨU VÀ LƯU VÀO DATABASE ---
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        sql = """
            INSERT INTO Users (full_name, username, password_hash, bank_account, bank_code, role) 
            VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(sql, (full_name, email, hashed_pw, 'CHUA_CAP_NHAT', 'CHUA_CAP_NHAT', 'USER'))
        conn.commit()
        
        print("✅ [DEBUG ĐĂNG KÝ] Đã nạp User mới vào SQL Server thành công.")
        return jsonify({"success": True, "message": "Đăng ký thành công!"}), 200
        
    except Exception as e:
        print(f"❌ Lỗi Đăng ký: {e}")
        return jsonify({"success": False, "message": "Lỗi hệ thống"}), 500
    finally:
        conn.close()


# ==========================================================
# 2. API ĐĂNG NHẬP (So sánh mã băm Bcrypt & Thiết lập Session)
# ==========================================================
@auth_bp.route('/api/login', methods=['POST'])
def login_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    conn = db.get_connection()
    if not conn:
        return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500
        
    try:
        cursor = conn.cursor()
        
        cursor.execute("SELECT user_id, password_hash, bank_account, bank_code, full_name, role, status, short_name FROM Users WHERE username = ? OR full_name = ?", (username, username))
        user = cursor.fetchone()
        
        if user:
            # KIỂM TRA TRẠNG THÁI TÀI KHOẢN TRƯỚC KHI SO SÁNH MẬT KHẨU
            account_status = user[6]
            if account_status == 'SUSPENDED':
                return jsonify({"success": False, "message": "Tài khoản đang bị tạm khóa để xác minh"}), 403
            elif account_status == 'BANNED':
                return jsonify({"success": False, "message": "Tài khoản đã bị cấm do vi phạm chính sách"}), 403
                
            hashed_pw_in_db = user[1].encode('utf-8')
            
            if bcrypt.checkpw(password.encode('utf-8'), hashed_pw_in_db):
                # Lưu session
                session.permanent = True
                session['user_id'] = user[0]
                raw_name = user[4] or username
                session['full_name'] = raw_name.title() if raw_name else "Người Dùng"
                session['short_name'] = user[7] if len(user) > 7 and user[7] else None
                session['role'] = user[5] or 'USER'
                
                return jsonify({
                    "success": True, 
                    "message": "Đăng nhập thành công!",
                    "role": session['role']
                }), 200
            else:
                return jsonify({"success": False, "message": "Mật khẩu không chính xác!"}), 401
        else:
            return jsonify({"success": False, "message": "Tài khoản không tồn tại!"}), 404
            
    except Exception as e:
        print(f"❌ Lỗi Đăng nhập: {e}")
        return jsonify({"success": False, "message": "Lỗi hệ thống"}), 500
    finally:
        conn.close()

# API ĐĂNG XUẤT
@auth_bp.route('/api/logout', methods=['GET'])
def logout():
    session.clear()
    return jsonify({"success": True})