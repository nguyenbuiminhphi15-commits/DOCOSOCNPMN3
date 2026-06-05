# DANH SÁCH CÔNG NGHỆ VÀ CÔNG CỤ SỬ DỤNG TRONG ĐỒ ÁN
*Dự án: Hệ thống thanh toán QR Secure kết hợp Trí tuệ nhân tạo (AI) và Blockchain*

Dưới đây là danh sách tổng hợp toàn bộ các ngôn ngữ, thư viện, Framework và công cụ phần mềm đã được sử dụng để xây dựng thành công hệ thống này. Bạn có thể sử dụng danh sách này để đưa vào phần "Môi trường phát triển" hoặc "Công nghệ áp dụng" trong quyển báo cáo đồ án.

---

## 1. Tầng Giao diện (Frontend / Client-side)
- **Ngôn ngữ cốt lõi:** HTML5, CSS3, JavaScript (Vanilla JS).
- **UI Framework:** **Bootstrap 5** - Thiết kế giao diện Reponsive (thích ứng di động), cung cấp hệ thống lưới (Grid system) và các Component (Card, Alert, Badge) hiện đại.
- **Biểu tượng (Icons):** Bootstrap Icons / FontAwesome.
- **Kỹ thuật xử lý bất đồng bộ:** Sử dụng **Fetch API** kết hợp **Short-polling** (`setInterval`) để liên tục "nghe ngóng" trạng thái đơn hàng (Ting Ting) mà không cần tải lại trang.
- **Thư viện cảnh báo (Alerts):** **SweetAlert2** - Dùng để tạo ra các hộp thoại (Popup) thông báo "TING TING! Đã nhận được tiền thanh toán!" mượt mà và trực quan trên màn hình thu ngân thay cho hộp thoại mặc định.
- **Hiển thị dữ liệu (Template Engine):** **Jinja2** - Dùng để đổ dữ liệu Real-time (Bảng cảnh báo AI, danh sách Users) từ Python xuống HTML.

## 2. Tầng Xử lý Logic (Backend / Server-side)
- **Ngôn ngữ cốt lõi:** **Python** (phiên bản >= 3.8).
- **Web Framework:** **Flask** - Micro-framework nhẹ gọn, hiệu năng cao, chuyên dùng để xây dựng RESTful API và điều hướng Webhook.
- **Bảo mật:** Thư viện `hmac`, `hashlib` của Python để xác thực chữ ký (Signature Validation).

## 3. Tầng Dữ liệu (Database Layer)
- **Hệ quản trị CSDL:** **Microsoft SQL Server (MSSQL)** - Quản lý 5 bảng dữ liệu cốt lõi (Users, Store_Orders, QR_Links, Transactions_Ledger, Hutech_Blockchain).
- **Trình điều khiển kết nối:** **ODBC Driver 17 for SQL Server** kết hợp thư viện Python `pyodbc`. Cho phép Backend giao tiếp với Database qua các câu lệnh SQL an toàn.

## 4. Trí tuệ Nhân tạo & Khoa học Dữ liệu (AI & Data Science)
- **Thuật toán cốt lõi:** **Isolation Forest** (Học máy không giám sát - Unsupervised Learning) dùng để phát hiện bất thường (Anomaly Detection) dựa trên số tiền và khung giờ.
- **Thư viện AI/ML:** **Scikit-learn** (`sklearn.ensemble`).
- **Xử lý số liệu:** Thư viện **Pandas** và **NumPy** dùng để chuẩn bị và định dạng Vector dữ liệu (Feature Engineering) trước khi đưa vào mô hình AI.

## 5. Công nghệ Chuỗi khối (Blockchain Technology)
- **Kiến trúc:** Sổ cái nội bộ bất biến (Internal Immutable Ledger).
- **Thuật toán Mật mã:** **SHA-256** (Secure Hash Algorithm).
- **Cơ chế đồng thuận:** **Proof of Work (PoW)** nhẹ - Máy chủ phải liên tục quay số ngẫu nhiên (đào Nonce) để tìm ra mã băm hợp lệ bắt đầu bằng các số `0000`, đảm bảo giao dịch một khi đã ghi nhận là không thể sửa đổi.

## 6. API Ngân hàng mở & Fintech (Third-Party Services)
- **Cổng thanh toán:** **SePay** - Cung cấp hạ tầng Tài khoản ảo (Virtual Account) liên kết mạng lưới Napas 247.
- **Cơ chế giao tiếp:** **Webhook API** - SePay chủ động gọi đến Server (POST Request) ngay khi có tiền đáp xuống tài khoản ngân hàng thực tế.

## 7. Môi trường phát triển & Công cụ mạng (Dev Tools & Networking)
- **Trình soạn thảo mã (IDE):** Visual Studio Code (VS Code).
- **Công cụ đường hầm (Tunneling/Reverse Proxy):** **Ngrok** - Chuyển tiếp cổng (Forward port) `localhost:5000` của máy tính cá nhân thành một Public IP chuẩn HTTPS trên Internet. Đóng vai trò tiên quyết để nhận được Webhook từ SePay.
- **Công cụ giả lập tấn công (Hacking/Testing Tool):** File mã hóa `hacker_tool.py` (Script Python nội bộ) tự phát triển để giả lập bắn các Payload Webhook mang số tiền sai lệch, phục vụ việc kiểm thử khả năng chống chịu của hệ thống AI.
- **Công cụ vẽ Sơ đồ chuẩn UML:** Mermaid.js, Draw.io, PlantUML.
