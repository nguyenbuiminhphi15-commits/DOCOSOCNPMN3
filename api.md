Cách mới: Bỏ chìa khóa vào két sắt (Lưu Database)
Đây là cách các hệ thống lớn hoạt động. Chìa khóa sẽ được giấu trong SQL Server. Luồng hoạt động chi tiết diễn ra theo 2 pha độc lập nhau:

⚙️ Pha 1: Cất chìa khóa (Người quản trị thao tác)
Pha này chỉ xảy ra khi bạn muốn cài đặt hoặc thay đổi Token mới.

Giao diện (Frontend): Bạn mở trang quản trị Web lên (Bước 4), dán cái Token mới lấy từ SePay vào ô input rồi bấm Lưu Cấu Hình.

Vận chuyển (API): Trình duyệt web sẽ đóng gói cái Token đó, gửi một lệnh POST đến địa chỉ /api/admin/update-token.

Lưu trữ (Backend): Hàm update_token() trong Python (Bước 3) sẽ đón lấy cái Token này, chạy xuống SQL Server và thực hiện lệnh UPDATE. Nó cất cái Token mới tinh vào ngăn tủ có tên là SEPAY_API_TOKEN trong bảng System_Settings (Bước 1).
(Xong! Chìa khóa đã được cất an toàn, không nằm trong file code nữa).

🚀 Pha 2: Lấy chìa khóa ra xài (Hệ thống tự động chạy)
Pha này xảy ra hàng chục lần mỗi ngày, cứ mỗi khi có khách mua hàng và Mắt thần cần đi kiểm tra tiền.

Khởi động Mắt thần: Khách chuyển tiền xong, hàm fetch_transaction_from_sepay (Bước 2) được gọi lên.

Mở két lấy chìa: Trước khi nó chạy sang hỏi máy chủ SePay, nó nhận ra nó đang... đi tay không. Lập tức, nó chạy xuống SQL Server, dùng lệnh SELECT mở đúng cái ngăn tủ SEPAY_API_TOKEN để lôi cái Token mà bạn đã cất ở Pha 1 ra.

Thi hành nhiệm vụ: Sau khi cầm Token trên tay, nó mới nhét Token đó vào Headers (với chữ Bearer ...) và tự tin chạy sang gõ cửa máy chủ SePay để lấy lịch sử giao dịch về.

💡 Tại sao quy trình này lại thể hiện đẳng cấp?
Khi xây dựng một nền tảng thương mại điện tử như đồ án Hutech Shop, tư duy này giúp hệ thống của bạn trở thành một phần mềm SaaS (Software as a Service - Phần mềm dạng dịch vụ) thực thụ:

Bảo mật tuyệt đối: Code hoàn toàn "sạch". Bạn có thể tự tin gửi toàn bộ file Python cho thầy cô hoặc bạn bè mà không sợ lộ mã số tài khoản hay Token cá nhân.

Khả năng thương mại hóa: Bạn code xong bộ Hutech Shop này 1 lần, sau đó đem bán hoặc sao chép cho 100 cửa hàng khác nhau. 100 người chủ cửa hàng đó không hề biết lập trình, họ chỉ việc đăng nhập vào web, tự dán Token của họ vào giao diện quản trị là hệ thống tự chạy. Không ai phải đụng vào file code app.py nữa.

---

## 🔥 Bản Nâng Cấp Tối Thượng: Kiến Trúc Đa Cửa Hàng (Multi-Tenant) & Mắt Thần Định Danh

Sau khi hoàn thành "Bỏ chìa khóa vào két sắt", hệ thống tiếp tục đối mặt với một bài toán thực tế của các chuỗi bán lẻ: **Làm sao để quản lý nhiều cửa hàng, mỗi cửa hàng xài một tài khoản ngân hàng và một API Key khác nhau?**

Nếu nhét tất cả API vào một cái "ngăn tủ" `System_Settings`, chúng sẽ đè lên nhau. Vì vậy, hệ thống đã được nâng cấp lên kiến trúc đa luồng (Multi-Tenant).

### 1. Bảng Dữ Liệu "Chùm Chìa Khóa" (`Sepay_Tokens`)
Thay vì dùng 1 ngăn tủ duy nhất, hệ thống tạo ra hẳn một bảng Database riêng biệt mang tên `Sepay_Tokens` (đóng vai trò như một chiếc móc khóa). Mỗi khi khai báo một cửa hàng mới trên giao diện Cấu hình, hệ thống sẽ chèn 1 dòng mới vào bảng này, đi kèm với 1 `id` tự động tăng. Thông tin lưu trữ bao gồm:
- **Tên gợi nhớ** (VD: Thanh toán Cửa hàng Quận 1)
- **Chuỗi Token thật** (Bị ẩn một phần trên giao diện)
- **Trạng thái** (Hoạt động / Tạm khóa)

### 2. Định Danh Mối Quan Hệ Lúc Khởi Tạo QR (Binding)
Ở giao diện **Tạo Mã QR**, thu ngân bắt buộc phải chọn xem mã QR này được xuất ra cho cửa hàng nào thông qua một danh sách sổ xuống.
Trình duyệt sẽ lấy cái `id` của cửa hàng đó (gọi là `token_id`) và bắn xuống Backend. Khi Backend lưu thông tin mã QR vào bảng `QR_Links`, nó lưu kèm luôn cột `token_id` này.
👉 Nghĩa là: **Mỗi mã QR ngay từ lúc chào đời đã ghi nhớ chính xác nó thuộc về cửa hàng nào (chìa khóa số mấy).**

### 3. Mắt Thần Kịch Bản 2: Truy Vết Cực Nhanh (Smart Polling)
Khi Mắt thần (Polling) khởi động để kiểm tra trạng thái thanh toán, nó hoạt động theo 3 bước cực kỳ tối ưu:
1. **Tra cứu Định danh:** Nó nhìn vào mã QR, chạy thẳng vào bảng `QR_Links` và móc ra cái `token_id`. (Vd: Nhận ra ngay đây là đơn của Cửa hàng Quận 1).
2. **Trích xuất Chìa khóa:** Nó cầm cái `token_id` đó chạy sang bảng `Sepay_Tokens` để móc đúng cái Token thực tế ra.
3. **Thẩm định tại SePay:** Nó nhét Token đó vào lệnh gọi mạng API (Header Bearer) rồi chạy qua máy chủ SePay.

**Tại sao đây lại là thiết kế chuẩn mực Doanh nghiệp (Enterprise)?**
Nếu thiết kế theo cách thông thường, hệ thống sẽ phải dùng vòng lặp `FOR` cầm từng chìa khóa chạy qua máy chủ SePay gõ cửa hỏi mù mờ: *"Cửa hàng 1 có nhận được tiền đơn này không? Không à. Thế Cửa hàng 2 có không?..."* (Rất tốn CPU và Network, dễ bị chặn do spam API).
Ngược lại, với Kịch Bản 2, hệ thống **bốc đúng chìa khóa và gõ đúng cửa ngay từ mili-giây đầu tiên**. Luồng thiết kế này giải quyết triệt để 2 vấn đề lớn nhất của FinTech: Tiết kiệm tối đa tài nguyên máy chủ và tránh tuyệt đối lỗi nhầm lẫn dòng tiền giữa hàng trăm chi nhánh khác nhau!

---

## 🛡️ Tích hợp Động cơ Blockchain (Core Engine): Lưu Trữ Bất Khả Xâm Phạm

Để đưa hệ thống lên đẳng cấp của một nền tảng FinTech/Web3 thực thụ, HUTECH Secure QR đã loại bỏ hoàn toàn khái niệm Sổ cái (Ledger) thông thường. Thay vào đó, mọi giao dịch thanh toán được niêm phong vào một chuỗi khối (Blockchain) nội bộ với 3 cơ chế cốt lõi sau:

### 1. Bảng Dữ Liệu Chuỗi Khối (`Hutech_Blockchain`)
Không giống như các bảng dữ liệu rời rạc, mỗi dòng dữ liệu trong bảng `Hutech_Blockchain` là một Khối (Block) liên kết chặt chẽ với nhau:
- **`block_index`**: Số thứ tự của Khối (VD: Khối số 1, Khối số 2).
- **`transactions_data`**: Dữ liệu giao dịch (Mã đơn hàng, Số tiền, Loại giao dịch) được đóng gói dưới định dạng JSON.
- **`previous_hash`**: Mã băm (Hash) của Khối liền trước nó. Đây là sợi dây xích nối các khối lại với nhau. Nếu Khối 1 bị thay đổi, Khối 2 sẽ lập tức trở nên vô hiệu.
- **`block_hash`**: Mã băm của chính Khối hiện tại.
- **`nonce`**: Con số ngẫu nhiên tìm được nhờ quá trình "Đào" (Proof of Work).

### 2. Thuật toán Bằng Chứng Công Việc (Proof of Work - PoW)
Thay vì dùng lệnh `INSERT` đơn giản và thụ động, mỗi khi có dòng tiền đổ về (thông qua Webhook hoặc Mắt thần), Server sẽ kích hoạt **Thuật toán Đào (Mining)** bên trong `blockchain_engine.py`:
- Server sẽ tiến hành băm (Hash SHA-256) toàn bộ thông tin của giao dịch mới + mã băm của khối cũ + một con số `nonce` chạy từ 0 trở lên.
- **Độ khó (Difficulty) = 4**: Vòng lặp sẽ chạy điên cuồng cho đến khi tìm được một con số `nonce` sao cho kết quả Mã băm sinh ra **bắt đầu bằng 4 con số 0** (VD: `0000a7b8f9...`).
- Sau khi "đào" thành công, Khối này mới được cấp phép ghi vào Database. Cơ chế này ngăn chặn việc Hacker spam hàng triệu giao dịch giả mạo vào CSDL trong 1 giây, vì CPU phải mất thời gian để "giải mã" (Đào) từng giao dịch một.

### 3. Cơ Chế Kiểm Toán Toàn Vẹn (Audit/Verify)
Điều làm nên sức mạnh của Blockchain chính là tính chất **Không Thể Đảo Ngược (Immutable)**. Hệ thống được trang bị hàm `verify_chain()` với khả năng quét lại toàn bộ lịch sử CSDL từ ngày đầu tiên thành lập (Genesis Block).
Hàm này sẽ hoạt động như một chuyên gia kiểm toán:
1. **Kiểm tra Móc xích:** Xác nhận xem `previous_hash` của Khối B có khớp y chang `block_hash` của Khối A hay không. Nếu đứt gãy -> Có kẻ đã xóa một giao dịch ở giữa.
2. **Kiểm tra Chữ ký:** Nó sẽ lấy dữ liệu giao dịch của Khối A băm lại từ đầu xem kết quả có ra đúng `block_hash` cũ không. Nếu Hacker lén lút sửa "10,000đ" thành "100,000đ", hàm băm sẽ thay đổi toàn bộ và Server sẽ báo động đỏ: `🚨 PHÁT HIỆN GIAN LẬN`.

Bằng cách áp dụng **Proof of Work** và **Chuỗi Khối**, đồ án HUTECH Shop không chỉ dừng lại ở việc bán hàng, mà nó đã sở hữu một "Trái tim FinTech" chuẩn mực, sẵn sàng đáp ứng yêu cầu khắt khe nhất về bảo mật dữ liệu!