import requests

def setup_sepay_webhook():
    print("🔄 Đang gửi yêu cầu cấu hình Webhook lên SePay...")
    
    # ==========================================
    # 1. ĐIỀN THÔNG TIN CỦA BẠN VÀO ĐÂY
    # ==========================================
    # Lấy ở trang my.sepay.vn -> Cài đặt -> API Token
    API_TOKEN = "ZIJEXELJ5J21YXWQQMVAGTDINL4NHQVE9YGCYSMUWCGSUKTIZO2DV1SOMUWAG7BE" 
    
    # Link ngrok đang chạy + đuôi API của bạn (Lưu ý: API trong code đang là /api/sepay/webhook)
    WEBHOOK_URL = "https://prowling-sappiness-slot.ngrok-free.dev/api/sepay/webhook"
    
    # ==========================================
    # 2. GỌI API THEO CHUẨN SEPAY BANK HUB
    # ==========================================
    url = "https://bankhub-api.sepay.vn/v1/webhook"
    
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # payload theo đúng chuẩn docs.sepay.vn
    payload = {
        "webhook_url": WEBHOOK_URL,
        "active": 1,              # 1 = Bật, 0 = Tắt
        "allow_events": ["*"]     # "*" = Lắng nghe mọi sự kiện tiền vào/ra
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        # Nếu HTTP Status trả về 200 là thao tác thành công
        if response.status_code == 200:
            print("✅ BINGO! SePay đã nhận Webhook của bạn thành công.")
            print("Chi tiết từ SePay:", response.json().get('data'))
        else:
            print(f"❌ Cấu hình thất bại (Mã lỗi {response.status_code}).")
            print("Chi tiết lỗi:", response.text)
            
    except Exception as e:
        print(f"❌ Lỗi kết nối mạng hoặc sai thư viện: {e}")

# Chạy lệnh
if __name__ == "__main__":
    setup_sepay_webhook()
