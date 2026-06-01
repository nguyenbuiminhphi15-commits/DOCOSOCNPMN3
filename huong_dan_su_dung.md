# HƯỚNG DẪN SỬ DỤNG HỆ THỐNG HUTECH SECURE QR

Tài liệu này hướng dẫn chi tiết cách vận hành và trải nghiệm hệ thống Thanh toán QR tích hợp AI & Blockchain, phục vụ cho việc trình diễn (Live-Demo) trong quá trình bảo vệ đồ án.

---

 
 tài khoản admin: tên nguyễn đình hòa
mk : hoa.123



## PHẦN 1: KHỞI ĐỘNG HỆ THỐNG (Dành cho Cài đặt)

Để hệ thống chạy mượt mà trên máy tính (hoặc máy của Giảng viên), thực hiện các bước sau:

1. **Khôi phục Cơ sở dữ liệu:**
   - Mở phần mềm **SQL Server Management Studio (SSMS)**.
   - Kéo thả file `Hutech_SecureQR.sql` vào màn hình SSMS và bấm **Execute (F5)** để tự động tạo Database `Hutech_SecureQR` và chèn sẵn dữ liệu.
2. **Khởi chạy Backend:**
   - Mở Terminal trong VS Code tại thư mục dự án.
   - Gõ lệnh: `python app.py`
   - Đợi dòng chữ `* Running on http://127.0.0.1:5000` xuất hiện.
3. **Mở Ngrok (Bắt buộc để test chuyển tiền thật):**
   - Mở phần mềm ngrok, gõ lệnh: `ngrok http 5000`.
   - Copy đường link HTTPS mà ngrok cấp (Ví dụ: `https://abcd.ngrok-free.app`) và dán vào phần cài đặt Webhook trên trang quản trị của SePay để hệ thống hứng được tiền về.

---

## PHẦN 2: HƯỚNG DẪN DÀNH CHO KHÁCH HÀNG (USER ROLE)

Khách hàng là người tương tác với giao diện mua sắm (Storefront) của hệ thống. Luồng trải nghiệm hoàn toàn tự động, khách hàng không cần tải app hay đăng nhập.

### Kịch bản 1: Thanh toán Hợp lệ (Luồng Xanh)
1. Mở trình duyệt, truy cập vào Cửa hàng và đi tới **Giỏ hàng** (`http://127.0.0.1:5000/cart`).
2. Nhập thông tin (Tên) và bấm **Tiến hành Thanh toán**.
3. Màn hình sẽ chuyển sang trang **Thanh toán QR**. Một mã VietQR sẽ được sinh ra tự động kèm thời gian đếm ngược 10 phút.
4. Khách hàng mở App Ngân hàng (Momo/Vietcombank...) quét mã QR và **CHUYỂN ĐÚNG SỐ TIỀN**.
5. Ngay khi bấm chuyển tiền thành công, **không cần F5 tải lại trang**, màn hình trình duyệt sẽ tự động bắn pháo hoa và hiển thị "Thanh toán Thành công!".

### Kịch bản 2: Gian lận hoặc Sai sót (Luồng Đỏ / Bị chặn)
Khách hàng lặp lại từ Bước 1 đến Bước 3 ở trên. Khi quét QR ở Bước 4, khách hàng cố tình "chơi chiêu":
- **Sửa số tiền:** Cố tình sửa số tiền nhỏ hơn giá trị đơn hàng (Ví dụ: Đơn 150.000đ nhưng chỉ chuyển 2.000đ để test).
- **Kết quả:** Tiền vẫn bị trừ trong tài khoản ngân hàng, nhưng màn hình trên web sẽ lập tức chuyển sang trạng thái cảnh báo màu vàng: **"Giao dịch cần đối soát. Vui lòng chờ CSKH liên hệ!"**.

---

## PHẦN 3: HƯỚNG DẪN DÀNH CHO QUẢN TRỊ VIÊN (ADMIN ROLE)

Quản trị viên là người nắm giữ quyền sinh sát, đứng sau hậu trường để quản lý rủi ro và sổ cái kế toán.

### 1. Đăng nhập hệ thống
- Truy cập vào đường dẫn: `http://127.0.0.1:5000/login`
- Đăng nhập bằng tài khoản Admin đã có sẵn trong cơ sở dữ liệu (Hoặc tạo tài khoản mới nếu cần).

### 2. Quản lý Bảng Điều khiển (Dashboard)
Ngay sau khi đăng nhập, Admin sẽ thấy **Admin Panel** (`/admin_panel`). Nơi đây quy tụ sức mạnh của Trí tuệ nhân tạo (AI):
- **Bảng Cảnh báo AI (AI Alerts):** Nếu ở Phần 2, Khách hàng cố tình chuyển sai tiền (Kịch bản 2), giao dịch đó sẽ lập tức bị giương cờ đỏ (FLAGGED) và nảy lên ngay trong bảng này. Bảng hiển thị rõ lý do: *"Sai lệch số tiền / Khung giờ dị thường"*.
- **Xử lý thủ công (Human-in-the-loop):** Admin có quyền kiểm tra tin nhắn ngân hàng thật. Nếu thấy khách hàng chuyển sai nhưng có lý do chính đáng, Admin có thể bấm nút **Duyệt thủ công** (Force Approve) màu xanh lá. Giao dịch sẽ lập tức được thông quan, khách hàng bên kia sẽ nhận được thông báo thành công.

### 3. Tạo QR thủ công (Tùy chọn)
- Truy cập tính năng **Tạo QR Nhận Tiền** (`/qr_generator`).
- Tính năng này dành cho các giao dịch ngoài luồng (Khách mua trực tiếp tại cửa tiệm, trả nợ...). Admin tự nhập số tiền và nội dung, sinh ra mã QR cho khách quét.

### 4. Giám sát Sổ cái Chuỗi khối (Blockchain Ledger)
- Toàn bộ mọi giao dịch (Dù là thành công tự động hay bị Admin chặn/duyệt) đều được tự động lưu vào Sổ cái Blockchain.
- Bất kỳ can thiệp nào vào CSDL (như sửa Data trực tiếp trong SQL Server) đều có thể bị phát hiện vì làm gãy mã băm SHA-256 (Current Hash sẽ không khớp với Previous Hash). Điều này chứng minh cho Hội đồng thấy dữ liệu tài chính của hệ thống là **Bất biến (Immutable)**.
