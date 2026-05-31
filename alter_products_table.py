import sys
sys.path.append('c:\\Users\\HOANG PC\\Source\\Repos\\Hutech_SecureQR')
from models.database_model import DatabaseModel

def alter_products_table():
    db = DatabaseModel()
    conn = db.get_connection()
    if not conn:
        print("Không thể kết nối CSDL")
        return
        
    try:
        cursor = conn.cursor()
        
        # Add category column if not exists
        cursor.execute("""
            IF NOT EXISTS (
                SELECT * FROM sys.columns 
                WHERE object_id = OBJECT_ID(N'[dbo].[Products]') AND name = 'category'
            )
            BEGIN
                ALTER TABLE Products ADD category NVARCHAR(100) DEFAULT N'Chưa phân loại'
            END
        """)
        
        # Change image column type to NVARCHAR(MAX) to store JSON arrays
        cursor.execute("""
            ALTER TABLE Products ALTER COLUMN image NVARCHAR(MAX)
        """)
        
        conn.commit()
        print("Cập nhật bảng Products thành công!")
    except Exception as e:
        print("Lỗi:", e)
    finally:
        conn.close()

if __name__ == "__main__":
    alter_products_table()
