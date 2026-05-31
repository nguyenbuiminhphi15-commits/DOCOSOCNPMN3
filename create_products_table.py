import sys
sys.path.append('c:\\Users\\HOANG PC\\Source\\Repos\\Hutech_SecureQR')
from models.database_model import DatabaseModel

def create_products_table():
    db = DatabaseModel()
    conn = db.get_connection()
    if not conn:
        print("Không thể kết nối CSDL")
        return
        
    try:
        cursor = conn.cursor()
        
        # Create table
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Products' and xtype='U')
            CREATE TABLE Products (
                id VARCHAR(50) PRIMARY KEY,
                name NVARCHAR(255) NOT NULL,
                price DECIMAL(18,2) NOT NULL,
                image VARCHAR(255),
                stock INT DEFAULT 0
            )
        """)
        
        # Insert mock data if table is empty
        cursor.execute("SELECT COUNT(*) FROM Products")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO Products (id, name, price, image, stock) VALUES
                ('SP001', N'Áo khoác HUTECH', 250000, 'https://bizweb.dktcdn.net/100/331/067/products/4-a82f34ec-d102-4bb3-8ccb-a36c92d5c197.jpg', 50),
                ('SP002', N'Balo sinh viên', 150000, 'https://product.hstatic.net/200000201725/product/balo-nam-nu-thoi-trang-han-quoc-chong-nuoc-tot_288ddffeaef04fc08470559ebbd8c0e7_master.jpg', 30)
            """)
        
        conn.commit()
        print("Đã tạo bảng Products và thêm dữ liệu mẫu thành công!")
    except Exception as e:
        print("Lỗi:", e)
    finally:
        conn.close()

if __name__ == "__main__":
    create_products_table()
