# File: app.py
from flask import Flask, render_template, session, redirect, url_for, request, jsonify
from functools import wraps
import os
import json
from werkzeug.utils import secure_filename
from models.database_model import DatabaseModel
from controllers.qr_controller import qr_bp
from controllers.auth_controller import auth_bp 
from controllers.webhook_controller import webhook_bp

app = Flask(__name__)
app.secret_key = 'hutech_secure_qr_secret_key_123'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = 'static/uploads/products'

# Khởi tạo class Database để test kết nối ngay khi chạy app
db = DatabaseModel()
db.test_connection()

app.register_blueprint(qr_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(webhook_bp)

# Decorators bảo vệ Route
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') not in ['ADMIN', 'STAFF']:
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def super_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'ADMIN':
            return jsonify({"success": False, "message": "Không có quyền thực hiện"}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    if 'user_id' in session:
        if session.get('role') == 'ADMIN':
            return redirect(url_for('admin_panel'))
        elif session.get('role') == 'USER':
            return redirect(url_for('customer_storefront'))
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    conn = db.get_connection()
    stats = {
        'total_revenue': 0,
        'avg_revenue': 0,
        'tx_count': 0,
        'inward_count': 0,
        'outward_count': 0,
        'chat_sent': 0,
        'webhook_sent': 0,
        'webhook_success': 0
    }
    
    from datetime import datetime
    import calendar
    
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    if start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
    else:
        now = datetime.now()
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        _, last_day = calendar.monthrange(now.year, now.month)
        end_date = now.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)
        
    date_label = f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"

    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    COUNT(TL.tx_id) as tx_count,
                    SUM(TL.actual_amount) as total_revenue
                FROM Transactions_Ledger TL
                JOIN QR_Links QL ON TL.qr_id = QL.qr_id
                WHERE QL.user_id = ? 
                  AND TL.created_at >= ? 
                  AND TL.created_at <= ?
            """, (session['user_id'], start_date, end_date))
            row = cursor.fetchone()
            if row:
                stats['tx_count'] = row[0] or 0
                stats['total_revenue'] = row[1] or 0
                stats['inward_count'] = row[0] or 0
                if stats['tx_count'] > 0:
                    stats['avg_revenue'] = int(stats['total_revenue'] / stats['tx_count'])
        except Exception as e:
            print("Lỗi lấy thống kê:", e)
            
        # Lấy 5 giao dịch gần nhất
        recent_txs = []
        try:
            cursor.execute("""
                SELECT TOP 5
                    TL.tx_id, 
                    TL.actual_amount, 
                    TL.created_at,
                    U.bank_account
                FROM Transactions_Ledger TL
                JOIN QR_Links QL ON TL.qr_id = QL.qr_id
                JOIN Users U ON QL.user_id = U.user_id
                WHERE U.user_id = ?
                  AND TL.created_at >= ? 
                  AND TL.created_at <= ?
                ORDER BY TL.created_at DESC
            """, (session['user_id'], start_date, end_date))
            for row in cursor.fetchall():
                recent_txs.append({
                    "id": row[0],
                    "amount": row[1] or 0,
                    "created_at": row[2].strftime("%d/%m/%Y %H:%M:%S") if row[2] else "",
                    "account": row[3] or ""
                })
        except Exception as e:
            print("Lỗi lấy giao dịch gần đây:", e)
        finally:
            conn.close()
            
    # Tính toán Max Value cho biểu đồ (mặc định tối thiểu 100,000 đ)
    max_chart_val = max(100000, stats['total_revenue'] * 1.2)
    # Làm tròn lên hàng chục nghìn
    import math
    max_chart_val = math.ceil(max_chart_val / 10000) * 10000

    return render_template('dashboard.html', stats=stats, recent_txs=recent_txs, max_chart_val=max_chart_val, date_label=date_label, start_date=start_date.strftime('%Y-%m-%d'), end_date=end_date.strftime('%Y-%m-%d'))

@app.route('/register')
def register():
    return render_template('register.html')

# Create QR route
@app.route('/qr-generator')
@login_required
def qr_generator():
    conn = db.get_connection()
    tokens = []
    user_bank = None
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, token_name FROM Sepay_Tokens WHERE is_active = 1 ORDER BY created_at DESC")
            for row in cursor.fetchall():
                tokens.append({"id": row[0], "name": row[1]})
                
            cursor.execute("SELECT bank_code, bank_account, full_name FROM Users WHERE user_id = ?", (session['user_id'],))
            row = cursor.fetchone()
            if row and row[1]:
                user_bank = {
                    'bank_code': row[0],
                    'bank_account': row[1],
                    'full_name': row[2] or 'Chưa cập nhật'
                }
        except Exception as e:
            print("Error fetching tokens:", e)
        finally:
            conn.close()
    return render_template('qr_generator.html', tokens=tokens, user_bank=user_bank)

@app.route('/account')
@login_required
def account():
    return render_template('account.html')

@app.route('/users')
@login_required
def users():
    return render_template('users.html')

@app.route('/statistics')
@login_required
def statistics():
    return render_template('statistics.html')

@app.route('/bank')
@login_required
def bank():
    conn = db.get_connection()
    user_bank = None
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT bank_code, bank_account, full_name FROM Users WHERE user_id = ?", (session['user_id'],))
            row = cursor.fetchone()
            if row and row[1]:
                user_bank = {
                    'bank_code': row[0],
                    'bank_account': row[1],
                    'full_name': row[2] or 'Chưa cập nhật'
                }
        except Exception as e:
            print("Lỗi lấy thông tin ngân hàng:", e)
        finally:
            conn.close()
    return render_template('bank.html', user_bank=user_bank)

@app.route('/api/update-bank', methods=['POST'])
@login_required
def update_bank():
    data = request.json
    bank_code = data.get('bank_code')
    bank_account = data.get('bank_account')
    
    if not bank_code or not bank_account:
        return jsonify({"success": False, "message": "Thiếu thông tin ngân hàng"}), 400
        
    conn = db.get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE Users SET bank_code = ?, bank_account = ? WHERE user_id = ?", 
                           (bank_code, bank_account, session['user_id']))
            conn.commit()
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
        finally:
            conn.close()
    return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

@app.route('/bank_detail')
@login_required
def bank_detail():
    return render_template('bank_detail.html')

@app.route('/bank_settings')
@login_required
def bank_settings():
    return render_template('bank_settings.html')

@app.route('/upgrade')
@login_required
def upgrade():
    return render_template('upgrade.html')

@app.route('/company_profile')
@login_required
def company_profile():
    return render_template('company_profile.html')

@app.route('/api/update_profile', methods=['POST'])
@login_required
def update_profile():
    data = request.json
    full_name = data.get('full_name', '').strip().title()
    short_name = data.get('short_name', '').strip()
    
    if not full_name or not short_name:
        return jsonify({"success": False, "message": "Vui lòng nhập đầy đủ thông tin"}), 400
        
    conn = db.get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE Users SET full_name = ?, short_name = ? WHERE user_id = ?", 
                           (full_name, short_name, session['user_id']))
            conn.commit()
            
            # Cập nhật session
            session['full_name'] = full_name
            session['short_name'] = short_name
            
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
        finally:
            conn.close()
    return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

@app.route('/settings')
@admin_required
def settings():
    conn = db.get_connection()
    tokens = []
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, token_name, token_string, is_active FROM Sepay_Tokens ORDER BY created_at DESC")
            for row in cursor.fetchall():
                tokens.append({
                    "id": row[0],
                    "name": row[1],
                    "token": row[2],
                    "status": "ACTIVE" if row[3] else "LOCKED"
                })
        except Exception as e:
            print("Error fetching settings:", e)
        finally:
            conn.close()
    return render_template('settings.html', tokens=tokens)

@app.route('/transactions')
@login_required
def transactions():
    conn = db.get_connection()
    user_bank = None
    txs = []
    if conn:
        try:
            cursor = conn.cursor()
            # Lấy thông tin tài khoản ngân hàng của user
            cursor.execute("SELECT bank_code, bank_account, full_name FROM Users WHERE user_id = ?", (session['user_id'],))
            row = cursor.fetchone()
            if row and row[1]:
                user_bank = {
                    'bank_code': row[0],
                    'bank_account': row[1],
                    'full_name': row[2] or 'Chưa cập nhật'
                }
            
            # Lấy danh sách giao dịch
            query = """
                SELECT 
                    TL.tx_id, 
                    TL.created_at, 
                    U.bank_account, 
                    U.bank_code,
                    QL.account_no, 
                    TL.actual_amount, 
                    TL.transfer_content,
                    TL.block_hash,
                    TL.status,
                    QL.qr_id
                FROM Transactions_Ledger TL
                JOIN QR_Links QL ON TL.qr_id = QL.qr_id
                JOIN Users U ON QL.user_id = U.user_id
                WHERE U.user_id = ?
                ORDER BY TL.created_at DESC
            """
            cursor.execute(query, (session['user_id'],))
            for tx_row in cursor.fetchall():
                txs.append({
                    "id": tx_row[0],
                    "created_at": tx_row[1].strftime("%d/%m/%Y %H:%M:%S") if tx_row[1] else "",
                    "bank_account": tx_row[2] or "",
                    "bank_code": tx_row[3] or "",
                    "virtual_account": tx_row[4] or "",
                    "amount": tx_row[5] or 0,
                    "description": tx_row[6] or "",
                    "reference": tx_row[7] or "",
                    "status": tx_row[8] or "",
                    "qr_id": tx_row[9] or ""
                })
        except Exception as e:
            print("Error fetching transactions:", e)
        finally:
            conn.close()
    return render_template('transactions.html', user_bank=user_bank, transactions=txs)

@app.route('/blockchain')
@admin_required
def blockchain():
    conn = db.get_connection()
    blocks = []
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT block_index, timestamp, transactions_data, nonce, previous_hash, block_hash FROM Hutech_Blockchain ORDER BY block_index DESC")
            for row in cursor.fetchall():
                blocks.append({
                    "index": row[0],
                    "timestamp": row[1],
                    "data": row[2],
                    "nonce": row[3],
                    "previous_hash": row[4],
                    "block_hash": row[5]
                })
        except Exception as e:
            print("Error fetching blockchain:", e)
        finally:
            conn.close()
    return render_template('blockchain.html', blocks=blocks)

# Admin Panel
@app.route('/admin_panel')
@admin_required
def admin_panel():
    conn = db.get_connection()
    users_data = []
    ai_alerts = [] # Mảng chứa danh sách giao dịch dị thường từ AI
    
    if conn:
        try:
            cursor = conn.cursor()
            # 1. Giữ nguyên đoạn lấy danh sách người dùng cũ của bạn
            cursor.execute("SELECT user_id, full_name, username, role, status FROM Users ORDER BY user_id DESC")
            rows = cursor.fetchall()
            for row in rows:
                users_data.append({
                    'user_id': row[0],
                    'full_name': row[1] if row[1] else 'Chưa cập nhật',
                    'email': row[2],
                    'role': row[3],
                    'status': row[4] if row[4] else 'ACTIVE'
                })
                
            # 2. BỔ SUNG: Truy vấn các đơn hàng bị AI gắn cờ đỏ (FLAGGED) từ Store_Orders
            cursor.execute("""
                SELECT id, customer_name, amount, created_at 
                FROM Store_Orders 
                WHERE status = 'FLAGGED' 
                ORDER BY created_at DESC
            """)
            for row in cursor.fetchall():
                ai_alerts.append({
                    'order_code': row[0],
                    'customer_name': row[1] or 'Khách vãng lai',
                    'amount': int(row[2]),
                    'time': row[3].strftime("%H:%M:%S — %d/%m/%Y") if row[3] else "Vừa xong",
                    'reason': "Isolation Forest phát hiện dấu hiệu bất thường về số tiền hoặc khung giờ"
                })
                
        except Exception as e:
            print("Lỗi lấy dữ liệu Admin:", e)
        finally:
            conn.close()
            
    # Đếm số lượng cảnh báo để hiển thị lên thẻ Warning màu vàng ở Dashboard
    ai_alert_count = len(ai_alerts)

    # Truyền thêm biến ai_alerts và ai_alert_count ra ngoài giao diện HTML
    return render_template('admin_panel.html', 
                           users=users_data, 
                           ai_alerts=ai_alerts, 
                           ai_alert_count=ai_alert_count)

@app.route('/api/admin/toggle_status', methods=['POST'])
@admin_required
def toggle_status():
    data = request.json
    user_id = data.get('user_id')
    new_status = data.get('status')
    
    conn = db.get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE Users SET status = ? WHERE user_id = ?", (new_status, user_id))
            conn.commit()
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
        finally:
            conn.close()
    return jsonify({"success": False, "message": "Database error"}), 500

@app.route('/api/admin/change_role', methods=['POST'])
@super_admin_required
def change_role():
    data = request.json
    user_id = data.get('user_id')
    new_role = data.get('role')
    
    conn = db.get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE Users SET role = ? WHERE user_id = ?", (new_role, user_id))
            conn.commit()
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
        finally:
            conn.close()
    return jsonify({"success": False, "message": "Database error"}), 500

# --- CRUD Products ---
@app.route('/api/admin/products', methods=['GET'])
@admin_required
def get_products():
    conn = db.get_connection()
    products = []
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, price, image, stock, category FROM Products")
            for row in cursor.fetchall():
                images = []
                try:
                    images = json.loads(row[3]) if row[3] else []
                except:
                    images = [row[3]] if row[3] else []
                
                products.append({
                    "id": row[0],
                    "name": row[1],
                    "price": float(row[2]),
                    "image": images[0] if images else "",
                    "images": images,
                    "stock": row[4],
                    "category": row[5]
                })
        except Exception as e:
            print("Lỗi get_products:", e)
        finally:
            conn.close()
    return jsonify({"success": True, "data": products})

@app.route('/api/admin/products', methods=['POST'])
@admin_required
def add_product():
    p_id = request.form.get('id')
    name = request.form.get('name')
    price = request.form.get('price')
    stock = request.form.get('stock', 0)
    category = request.form.get('category', 'Chưa phân loại')
    
    # Handle files
    image_paths = []
    if 'images' in request.files:
        files = request.files.getlist('images')
        for file in files:
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                # Ensure directory exists
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                # Store relative path for web
                image_paths.append(f"/static/uploads/products/{filename}")
                
    images_json = json.dumps(image_paths)
    
    conn = db.get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Products (id, name, price, image, stock, category) VALUES (?, ?, ?, ?, ?, ?)",
                           (p_id, name, price, images_json, stock, category))
            conn.commit()
            return jsonify({"success": True, "message": "Đã thêm sản phẩm thành công!"})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
        finally:
            conn.close()
    return jsonify({"success": False, "message": "Lỗi CSDL"}), 500

@app.route('/api/admin/products/<product_id>', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    conn = db.get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Products WHERE id = ?", (product_id,))
            conn.commit()
            return jsonify({"success": True, "message": "Đã xóa sản phẩm!"})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
        finally:
            conn.close()
    return jsonify({"success": False, "message": "Lỗi CSDL"}), 500

@app.route('/products_manage')
@admin_required
def products_manage():
    return render_template('products_manage.html')

@app.route('/shop', methods=['GET'])
@login_required
def customer_storefront():
    conn = db.get_connection()
    products = []
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, price, image, stock, category FROM Products")
            for row in cursor.fetchall():
                images = []
                try:
                    images = json.loads(row[3]) if row[3] else []
                except:
                    images = [row[3]] if row[3] else []
                    
                products.append({
                    "id": row[0],
                    "name": row[1],
                    "price": int(row[2]),
                    "image": images[0] if images else "https://via.placeholder.com/300x220?text=No+Image",
                    "stock": row[4],
                    "category": row[5]
                })
        except Exception as e:
            print("Lỗi get_products_shop:", e)
        finally:
            conn.close()
    return render_template('shop.html', products=products)

@app.route('/shop/<product_id>', methods=['GET'])
@login_required
def product_detail(product_id):
    conn = db.get_connection()
    product = None
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, price, image, stock, category FROM Products WHERE id = ?", (product_id,))
            row = cursor.fetchone()
            if row:
                images = []
                try:
                    images = json.loads(row[3]) if row[3] else []
                except:
                    images = [row[3]] if row[3] else []
                    
                product = {
                    "id": row[0],
                    "name": row[1],
                    "price": int(row[2]),
                    "images": images if images else ["https://via.placeholder.com/600x400?text=No+Image"],
                    "stock": row[4],
                    "category": row[5]
                }
        except Exception as e:
            print("Lỗi get_product_detail:", e)
        finally:
            conn.close()
            
    if not product:
        return "Sản phẩm không tồn tại", 404
        
    return render_template('product_detail.html', p=product)

@app.route('/cart', methods=['GET'])
@login_required
def cart_page():
    return render_template('cart.html')

@app.route('/api/checkout', methods=['POST'])
@login_required
def api_checkout():
    data = request.json
    cart_items = data.get('cart_items', [])
    customer = data.get('customer_info', {})
    
    if not cart_items or not customer:
        return jsonify({"success": False, "message": "Giỏ hàng hoặc thông tin khách hàng không hợp lệ"}), 400
        
    conn = db.get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            total_amount = 0
            order_details = []
            
            # 1. Tính tổng tiền an toàn từ Database và trừ Tồn kho
            for item in cart_items:
                product_id = item.get('id')
                qty = item.get('qty', 1)
                
                cursor.execute("SELECT price, stock, name FROM Products WHERE id = ?", (product_id,))
                product = cursor.fetchone()
                
                if not product:
                    conn.rollback()
                    return jsonify({"success": False, "message": f"Sản phẩm {product_id} không tồn tại"}), 404
                    
                real_price = product[0]
                stock = product[1]
                name = product[2]
                
                if stock < qty:
                    conn.rollback()
                    return jsonify({"success": False, "message": f"Sản phẩm {name} không đủ số lượng!"}), 400
                    
                cursor.execute("UPDATE Products SET stock = stock - ? WHERE id = ?", (qty, product_id))
                
                line_total = real_price * qty
                total_amount += line_total
                
                order_details.append({
                    "id": product_id,
                    "name": name,
                    "qty": qty,
                    "price": int(real_price)
                })
            
            # 3. Sinh mã đơn hàng
            import random
            order_code = f"HUTECH_CART_{random.randint(10000, 99999)}"
            
            # 4. Lưu đơn hàng vào DB với trạng thái 'PENDING'
            import json
            cursor.execute("""
                INSERT INTO Store_Orders (id, product_id, amount, status, created_at, expires_at, payer_ip, details, customer_name, customer_phone, customer_address) 
                VALUES (?, '', ?, 'PENDING', GETDATE(), DATEADD(minute, 10, GETDATE()), ?, ?, ?, ?, ?)
            """, (
                order_code, 
                total_amount, 
                request.remote_addr or '127.0.0.1', 
                json.dumps(order_details),
                customer.get('name', ''),
                customer.get('phone', ''),
                customer.get('address', '')
            ))
            
            # ==========================================================
            # BƯỚC MỚI: LƯU VÀO SỔ CÁI GIAO DỊCH ĐỂ HIỆN LÊN TRANG ADMIN
            # ==========================================================
            bank_acc = "96247HOATHUI" 
            
            # Lấy user_id (Bảo vệ trường hợp khách mua không có session admin)
            admin_user_id = session.get('user_id', 1) 
            
            import hmac
            import hashlib
            secret_key = b"HUTECH_SECURE_SECRET_KEY_2026"
            data_to_sign = f"{order_code}|{total_amount}".encode('utf-8')
            signature = hmac.new(secret_key, data_to_sign, hashlib.sha256).hexdigest()
            
            # 1. Cấp quyền sở hữu mã QR này cho Admin
            cursor.execute("""
                INSERT INTO QR_Links (qr_id, user_id, expected_amount, status, created_at, account_no, hmac_signature) 
                VALUES (?, ?, ?, 'ACTIVE', GETDATE(), ?, ?)
            """, (order_code, admin_user_id, total_amount, bank_acc, signature))
            
            # 2. Tạo một dòng Giao dịch Đang chờ (PENDING)
            cursor.execute("""
                INSERT INTO Transactions_Ledger (tx_id, qr_id, actual_amount, transfer_content, status, created_at, block_hash, payer_ip, ai_risk_score)
                VALUES (?, ?, ?, ?, 'PENDING', GETDATE(), 'WAITING_BLOCK', ?, 0)
            """, (f"WAIT_{order_code}", order_code, total_amount, order_code, request.remote_addr or '127.0.0.1'))
            # ==========================================================
            
            conn.commit()
            
            # 5. Server tự tạo link QR Tài khoản ảo SePay chính xác
            bank_name = "BIDV"
            bank_acc = "96247HOATHUI" # Mã tài khoản ảo SePay cấp cho bạn
            
            # Thay thế sang API qr.sepay.vn để tự động sinh QR giống trang quản trị
            qr_url = f"https://qr.sepay.vn/img?bank={bank_name}&acc={bank_acc}&amount={int(total_amount)}&des={order_code}&template=compact&mask=1"
            
            # Tính thời gian hết hạn trả về cho FE
            return jsonify({
                "success": True, 
                "qr_url": qr_url, 
                "order_code": order_code,
                "price": int(total_amount)
            })
            
        except Exception as e:
            conn.rollback()
            return jsonify({"success": False, "message": str(e)}), 500
        finally:
            conn.close()
            
    return jsonify({"success": False, "message": "Lỗi CSDL"}), 500

@app.route('/api/order/status/<order_code>', methods=['GET'])
def check_order_status(order_code):
    conn = db.get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT status, expires_at, details, product_id FROM Store_Orders WHERE id = ?", (order_code,))
            order = cursor.fetchone()
            
            if not order:
                return jsonify({"success": False, "message": "Không tìm thấy đơn hàng"}), 404
                
            status = order[0]
            expires_at = order[1]
            details_json = order[2]
            product_id = order[3]
            
            # Kiểm tra hết hạn nếu đang PENDING
            import datetime
            now = datetime.datetime.now()
            if status == 'PENDING' and now > expires_at:
                # Hủy đơn và hoàn kho
                cursor.execute("UPDATE Store_Orders SET status = 'CANCELED' WHERE id = ?", (order_code,))
                
                # Hoàn kho
                if details_json:
                    import json
                    try:
                        details = json.loads(details_json)
                        for item in details:
                            cursor.execute("UPDATE Products SET stock = stock + ? WHERE id = ?", (item['qty'], item['id']))
                    except:
                        pass
                elif product_id:
                    cursor.execute("UPDATE Products SET stock = stock + 1 WHERE id = ?", (product_id,))
                    
                conn.commit()
                status = 'CANCELED'
                
            return jsonify({"success": True, "status": status})
            
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
        finally:
            conn.close()
    return jsonify({"success": False, "message": "Lỗi CSDL"}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
