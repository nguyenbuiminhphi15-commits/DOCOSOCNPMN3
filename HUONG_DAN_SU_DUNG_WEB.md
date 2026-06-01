# Hướng Dẫn Sử Dụng Hệ Thống Fraud Detection & Blockchain Explorer

Tài liệu này hướng dẫn cách kiểm thử luồng hoạt động của hệ thống AI phát hiện gian lận và cách xem dữ liệu được lưu vết (Audit Trail) trên Blockchain nội bộ.

---

## 🚀 Bước 1: Khởi động hệ thống
1. Đảm bảo bạn đã cài đặt đủ các thư viện Python (FastAPI, Uvicorn, Scikit-learn, Pandas...).
2. Mở cửa sổ Terminal/Command Prompt tại thư mục gốc của dự án (`DOANCOSOCNPM`).
3. Chạy lệnh khởi động máy chủ Backend:
   ```bash
   python -m uvicorn app.main:app --reload
   ```
4. Nếu thấy dòng chữ `Application startup complete`, hệ thống đã sẵn sàng hoạt động tại địa chỉ `http://127.0.0.1:8000`.

Các trang giao diện chính:
- **Trang Đăng Nhập:** `http://127.0.0.1:8000/`
- **Dashboard Tổng Quan:** `http://127.0.0.1:8000/dashboard`
- **Danh sách Giao Dịch & Quét AI:** `http://127.0.0.1:8000/transactions`
- **Sổ cái Blockchain nội bộ:** `http://127.0.0.1:8000/blockchain`
- **Swagger UI (Test API):** `http://127.0.0.1:8000/docs`

---

## 🧪 Bước 2: Gửi Giao Dịch Thử Nghiệm (Test AI)
Hệ thống sử dụng **Swagger UI** làm giao diện gửi dữ liệu mô phỏng hoạt động từ App Ngân hàng.
1. Mở trình duyệt, truy cập vào trang Swagger: **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**
2. Cuộn xuống phần **Hệ thống lõi phân tích rủi ro AI**, bấm vào API có tên `POST /api/ai/analyze`.
3. Bấm nút **Try it out** ở góc phải màn hình.
4. Nhập dữ liệu giao dịch giả định vào khung `Request body`. 
   *Ví dụ một giao dịch rút tiền lớn bất thường (Rủi ro cao):*
   ```json
   1. Kịch bản "Giao dịch Sạch" (An toàn)
Dữ liệu mô phỏng người dùng bình thường, giao dịch trong giờ hành chính, thiết bị quen thuộc.

JSON
{
  "type": "TRANSFER",
  "amount": 500000.0,
  "oldbalanceOrg": 5000000.0,
  "newbalanceOrig": 4500000.0,
  "oldbalanceDest": 1000000.0,
  "newbalanceDest": 1500000.0,
  "tx_frequency_1m": 1,
  "login_hour": 10,
  "is_new_device": 0,
  "is_vpn_proxy": 0,
  "failed_login_count": 0,
  "distance_from_last_login": 1.0,
  "time_since_last_login": 3600.0
}
2. Kịch bản "Rủi ro Cao" (Cảnh báo & Yêu cầu OTP)
Dữ liệu mô phỏng việc đăng nhập từ thiết bị lạ, sử dụng VPN, tần suất giao dịch dày.

JSON
{
  "type": "CASH_OUT",
  "amount": 15000000.0,
  "oldbalanceOrg": 20000000.0,
  "newbalanceOrig": 5000000.0,
  "oldbalanceDest": 0.0,
  "newbalanceDest": 15000000.0,
  "tx_frequency_1m": 5,
  "login_hour": 14,
  "is_new_device": 1,
  "is_vpn_proxy": 1,
  "failed_login_count": 2,
  "distance_from_last_login": 10.0,
  "time_since_last_login": 300.0
}
3. Kịch bản "Nguy cấp" (Chặn giao dịch & Khắc log Blockchain)
Dữ liệu mô phỏng hành vi Impossible Travel (vị trí thay đổi bất khả thi), giao dịch lúc 3h sáng, sai lệch số dư.

JSON
{
  "type": "TRANSFER",
  "amount": 90000000.0,
  "oldbalanceOrg": 100000000.0,
  "newbalanceOrig": 0.0,
  "oldbalanceDest": 0.0,
  "newbalanceDest": 90000000.0,
  "tx_frequency_1m": 1,
  "login_hour": 3,
  "is_new_device": 1,
  "is_vpn_proxy": 1,
  "failed_login_count": 0,
  "distance_from_last_login": 2000.0,
  "time_since_last_login": 10.0
}
   ```

Nội dung JSON cho từng trường hợp
T



C-01: Giao dịch chuẩn
JSON
{"type": "TRANSFER", "amount": 500000.0, "oldbalanceOrg": 5000000.0, "newbalanceOrig": 4500000.0, "oldbalanceDest": 1000000.0, "newbalanceDest": 1500000.0, "tx_frequency_1m": 1, "login_hour": 10, "is_new_device": 0, "is_vpn_proxy": 0, "failed_login_count": 0, "distance_from_last_login": 1.0, "time_since_last_login": 3600.0}




TC-02: Spam giao dịch
JSON
{"type": "TRANSFER", "amount": 500000.0, "oldbalanceOrg": 5000000.0, "newbalanceOrig": 4500000.0, "oldbalanceDest": 1000000.0, "newbalanceDest": 1500000.0, "tx_frequency_1m": 4, "login_hour": 10, "is_new_device": 0, "is_vpn_proxy": 0, "failed_login_count": 0, "distance_from_last_login": 1.0, "time_since_last_login": 10.0}




TC-03: Đăng nhập lạ (Thiết bị mới + VPN)
JSON
{"type": "TRANSFER", "amount": 25000000.0, "oldbalanceOrg": 50000000.0, "newbalanceOrig": 25000000.0, "oldbalanceDest": 0.0, "newbalanceDest": 25000000.0, "tx_frequency_1m": 1, "login_hour": 10, "is_new_device": 1, "is_vpn_proxy": 1, "failed_login_count": 0, "distance_from_last_login": 10.0, "time_since_last_login": 300.0}




TC-04: Brute Force (Đăng nhập sai nhiều lần)
JSON
{"type": "TRANSFER", "amount": 1000000.0, "oldbalanceOrg": 5000000.0, "newbalanceOrig": 4000000.0, "oldbalanceDest": 0.0, "newbalanceDest": 1000000.0, "tx_frequency_1m": 1, "login_hour": 10, "is_new_device": 0, "is_vpn_proxy": 0, "failed_login_count": 6, "distance_from_last_login": 1.0, "time_since_last_login": 3600.0}
TC-05: Impossible Travel (Di chuyển bất khả thi)
JSON
{"type": "TRANSFER", "amount": 10000000.0, "oldbalanceOrg": 50000000.0, "newbalanceOrig": 40000000.0, "oldbalanceDest": 0.0, "newbalanceDest": 10000000.0, "tx_frequency_1m": 1, "login_hour": 10, "is_new_device": 0, "is_vpn_proxy": 0, "failed_login_count": 0, "distance_from_last_login": 500.0, "time_since_last_login": 5.0}





TC-06: Rút cạn số dư (Tẩu tán tài sản)
JSON
{"type": "CASH_OUT", "amount": 15000000.0, "oldbalanceOrg": 15000000.0, "newbalanceOrig": 0.0, "oldbalanceDest": 0.0, "newbalanceDest": 15000000.0, "tx_frequency_1m": 1, "login_hour": 12, "is_new_device": 0, "is_vpn_proxy": 0, "failed_login_count": 0, "distance_from_last_login": 1.0, "time_since_last_login": 3600.0}



TC-07: Lừa đảo nửa đêm (Giao dịch lớn, giờ lạ)
JSON
{"type": "TRANSFER", "amount": 90000000.0, "oldbalanceOrg": 100000000.0, "newbalanceOrig":

5. Bấm **Execute**. 
6. Kéo xuống phần `Response body` để xem AI chấm điểm rủi ro. Nếu thấy `alert_level` báo `HIGH` hoặc `CRITICAL`, tức là các mô hình Machine Learning đã phát hiện thành công gian lận!

---

## 🔗 Bước 3: Xem Dữ Liệu Trên Blockchain Explorer
Ngay khi AI phân tích xong một giao dịch, bất kể là giao dịch an toàn hay lừa đảo, nó đều được mã hóa bằng SHA-256 và nối vào chuỗi Blockchain nội bộ.
1. Mở một tab mới trên trình duyệt, truy cập: **[http://127.0.0.1:8000/blockchain](http://127.0.0.1:8000/blockchain)**
2. Trang **Sổ Cái Blockchain Nội Bộ** (Giao diện Dark Mode lấy cảm hứng từ Ganache) sẽ hiện ra.
3. Tại đây bạn sẽ thấy danh sách các khối (Block):
   - **Sổ cái gốc (Genesis Block):** Khối Khởi nguồn (Block 0), luôn tự động sinh ra khi Blockchain được khởi tạo lần đầu tiên.
   - **Các khối giao dịch (Block 1, 2, 3...):** Các khối mới sinh ra từ quá trình bạn test ở Bước 2. Chúng được sắp xếp mới nhất ở trên cùng.
4. **Cách đọc dữ liệu trên giao diện Blockchain:**
   - **MÃ BĂM KHỐI (BLOCK HASH):** Khóa bảo mật SHA-256 của toàn bộ khối.
   - **TX HASH:** Nằm ngay dưới Block Hash, đây là mã băm riêng của dữ liệu giao dịch đó (Tầng 4).
   - **THÔNG TIN GIAO DỊCH:** Cung cấp loại giao dịch (ví dụ: `[CASH_OUT]`), số tiền, và một **Huy hiệu (Badge)** thể hiện Nhãn rủi ro (`LOW`, `HIGH`, `CRITICAL`) do AI đánh giá.
5. Nếu bạn vừa qua Swagger bấm test thêm giao dịch mới, bạn chỉ cần quay lại trang Blockchain và bấm nút **LÀM MỚI** ở góc trên bên phải để tải dữ liệu khối mới nhất về.

---

## 💡 Mẹo Trả Lời Hội Đồng Bảo Vệ

**1. "Hệ thống lưu dữ liệu Blockchain này ở đâu? Có bị mất khi sập nguồn không?"**
> **Trả lời:** Không bị mất ạ. Khác với lưu tạm trên RAM, em đã viết cơ chế **Persistent Storage**. Mỗi khi có khối mới, hệ thống sẽ tự động append (ghi chèn) vào tệp lưu trữ cứng `ledger.json` trong thư mục dự án. Khi Server khởi động lại, Blockchain Engine sẽ tự động nạp lại (load) toàn bộ lịch sử từ file sổ cái này, y hệt cơ chế đồng bộ của một Node Blockchain thực tế.

**2. "Tại sao em không dùng mạng Ethereum thực hoặc nền tảng Ganache có sẵn?"**
> **Trả lời:** Em sử dụng Blockchain nội bộ do chính mình tự code vì các lý do sau:
> 1. **Tốc độ (Real-time):** Việc gọi API ra ngoài mạng Ethereum làm giảm tốc độ nhận diện gian lận. Hệ thống của em cần tốc độ xử lý tính bằng mili-giây.
> 2. **Kiểm soát hoàn toàn:** Em làm chủ được quy trình băm SHA-256 và lưu vết kiểm toán (Audit Trail) mà không bị phụ thuộc vào bên thứ 3.
> 3. **Bảo mật nội bộ:** Đây là dữ liệu giao dịch tài chính nhạy cảm, không cần thiết phải public lên mạng Public Blockchain, dùng Private Chain lưu vết tại máy chủ ngân hàng là kiến trúc thực tế nhất.

**3. "Tại sao giao diện Blockchain của em không có các thông số như Phí Gas, Hardfork?"**
> **Trả lời:** Các thông số đó chỉ tồn tại trên môi trường giả lập mạng Ethereum (ví dụ như Ganache). Hệ thống của em là một **Private Internal Ledger** (Sổ cái nội bộ riêng tư) tập trung vào nghiệp vụ truy xuất nguồn gốc và chống giả mạo logs, do đó khái niệm "Đào" (Mining) hay trả phí Gas là không tồn tại. Em đã thiết kế UI tinh gọn, tập trung hoàn toàn vào dữ liệu giao dịch.
