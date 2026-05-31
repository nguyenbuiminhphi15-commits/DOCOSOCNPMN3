# File: test_sepay.py
import requests

print("=== 🏦 CÔNG CỤ GIẢ LẬP SEPAY CHUYỂN TIỀN ===")

# Hệ thống sẽ dừng lại ở đây để chờ bạn nhập/dán mã QR vào
qr_id_nhap_vao = input("👉 Hãy dán mã QR giao dịch (VD: QR_1234ABCD) vào đây và nhấn Enter: ").strip()

payload = {
  "transferAmount": 50000,
  "transactionContent": f"{qr_id_nhap_vao} Thanh toan mua hang",
}

print(f"\n🚀 Đang bắn thông báo tiền về cho mã: {qr_id_nhap_vao}...")
res = requests.post("http://127.0.0.1:5000/api/webhook/sepay", json=payload)

print("✅ Server phản hồi:", res.json())