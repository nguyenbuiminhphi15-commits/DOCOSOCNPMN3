import sys
sys.path.append('c:\\Users\\HOANG PC\\Source\\Repos\\Hutech_SecureQR')
from models.database_model import DatabaseModel

def create_store_orders_table():
    db = DatabaseModel()
    conn = db.get_connection()
    if not conn:
        print("Không thể kết nối CSDL")
        return
        
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Store_Orders' and xtype='U')
            CREATE TABLE Store_Orders (
                id VARCHAR(50) PRIMARY KEY,
                product_id VARCHAR(50) NOT NULL,
                amount DECIMAL(18,2) NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
                created_at DATETIME DEFAULT GETDATE(),
                expires_at DATETIME,
                payer_ip VARCHAR(50)
            )
        """)
        
        conn.commit()
        print("Đã tạo bảng Store_Orders thành công!")
    except Exception as e:
        print("Lỗi:", e)
    finally:
        conn.close()

if __name__ == "__main__":
    create_store_orders_table()
