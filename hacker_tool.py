import requests
import threading
import time

URL = "http://127.0.0.1:5000/api/webhook/sepay"
PAYLOAD = {"transferAmount": 500000, "code": "HUTECH_DH001"}

def print_result(attack_name, response):
    if response.status_code == 200:
        print(f"✅ {attack_name}: Xuyên thủng thành công! -> {response.text}")
    else:
        print(f"🛑 {attack_name}: Bị AI CHẶN! -> HTTP {response.status_code} - {response.text}")

print("=== HỆ THỐNG MÔ PHỎNG TẤN CÔNG (DDoS TẦNG 7) ===")
print("1. Giao dịch Webhook bình thường")
print("2. Tấn công ngâm kết nối (Slowloris)")
print("3. Tấn công dội bom Request (HULK Flood)")
choice = input("\nChọn kịch bản Demo (1/2/3): ")

if choice == '1':
    print("\n👉 Đang gửi Webhook thanh toán bình thường...")
    res = requests.post(URL, json=PAYLOAD)
    print_result("Khách mua hàng", res)

elif choice == '2':
    print("\n👉 Đang kích hoạt Slowloris (Ngâm kết nối 65,000 ms)...")
    # Truyền header giả lập thời gian ngâm kết nối lâu
    headers = {"X-Simulate-Duration": "65000"} 
    res = requests.post(URL, json=PAYLOAD, headers=headers)
    print_result("Slowloris", res)

elif choice == '3':
    print("\n👉 Đang kích hoạt HULK Flood (Spam 50 Request/giây)...")
    
    # Hàm spam để tăng biến flow_packets_sec trên Server
    def spam_task():
        try:
            requests.post(URL, json=PAYLOAD)
        except: pass

    threads = []
    # Bắn 50 luồng cùng lúc
    for _ in range(50):
        t = threading.Thread(target=spam_task)
        t.start()
        threads.append(t)
    
    # Chờ đám clone bắn xong
    for t in threads:
        t.join()
        
    # Bắn phát súng cuối cùng để xem AI phản ứng ra sao
    res = requests.post(URL, json=PAYLOAD)
    print_result("HULK Flood", res)

else:
    print("Chọn sai kịch bản!")
