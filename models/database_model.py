# File: models/database_model.py
import pyodbc

class DatabaseModel:
    def __init__(self):
        # THAY ĐỔI TÊN SERVER Ở DÒNG DƯỚI CHO KHỚP VỚI MÁY CỦA BẠN
        # Ví dụ: 'localhost\\SQLEXPRESS' hoặc 'DESKTOP-ABC\\SQLEXPRESS'
        self.server = 'LAPTOP-NPGB1T0P' 
        self.database = 'Hutech_SecureQR'
        
        # Chuỗi kết nối sử dụng Windows Authentication (Không cần username/password)
        self.conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.server};DATABASE={self.database};Trusted_Connection=yes;'

    def get_connection(self):
        """Hàm mở kết nối đến SQL Server"""
        try:
            conn = pyodbc.connect(self.conn_str)
            return conn
        except pyodbc.Error as e:
            print(f"❌ Lỗi kết nối CSDL: {e}")
            return None

    def test_connection(self):
        """Hàm dùng để test xem ống nước đã thông chưa"""
        conn = self.get_connection()
        if conn:
            cursor = conn.cursor()
            # Thử query lấy ra tài khoản admin_phi vừa tạo lúc nãy
            cursor.execute("SELECT username, bank_account FROM Users WHERE username = 'admin_phi'")
            user = cursor.fetchone()
            
            if user:
                print(f"[OK] Connected to SQL Server! Found User: {user.username} (Bank: {user.bank_account})")
            else:
                print("[OK] Connected to SQL Server, but no users found.")
            
            conn.close()
            return True
        return False