# CHƯƠNG 6: HƯỚNG DẪN SỬ DỤNG VÀ THỰC NGHIỆM HỆ THỐNG

Chương này trình bày chi tiết về giao diện và cách thức vận hành hệ thống Hutech Secure QR ở hai góc độ: Người dùng cuối (Khách hàng) và Quản trị viên (Admin).

## 6.1. Hướng dẫn dành cho Khách hàng (User)

Luồng trải nghiệm của khách hàng được thiết kế hoàn toàn tự động, nhanh chóng và không yêu cầu đăng nhập hay cài đặt ứng dụng.

### 6.1.1. Cửa hàng trực tuyến (Storefront)
- Khách hàng truy cập vào trang Cửa hàng thông qua trình duyệt web.
- Tại đây, hệ thống hiển thị danh sách các sản phẩm đang được bán với đầy đủ thông tin: hình ảnh, tên sản phẩm, giá bán, và số lượng tồn kho.
- Khách hàng có thể chọn sản phẩm mong muốn và thêm vào giỏ hàng.

### 6.1.2. Giỏ hàng và Thanh toán
- Sau khi chọn xong sản phẩm, khách hàng chuyển đến trang **Giỏ hàng** (`/cart`).
- Khách hàng nhập thông tin cá nhân cơ bản (Tên, số điện thoại, địa chỉ giao hàng) và nhấn nút **Tiến hành Thanh toán**.
- Hệ thống sẽ chuyển sang giao diện thanh toán QR. Một mã **VietQR** đặc chuẩn được sinh ra tự động, tích hợp sẵn thông tin tài khoản ngân hàng thụ hưởng, số tiền chính xác cần thanh toán và nội dung chuyển khoản (chứa mã đơn hàng).
- Giao diện có đồng hồ đếm ngược 10 phút, tạo ra giới hạn thời gian thực hiện giao dịch để hệ thống giữ hàng (hold stock) an toàn.

### 6.1.3. Trải nghiệm Thanh toán Tự động
Khách hàng sử dụng ứng dụng Ngân hàng hoặc Ví điện tử (Momo, ZaloPay, Vietcombank...) quét mã QR được hiển thị trên màn hình.
- **Thanh toán Hợp lệ (Luồng Xanh):** Khách hàng chuyển ĐÚNG số tiền hiển thị. Hệ thống SePay sẽ hứng thông báo biến động số dư và gọi Webhook về máy chủ Hutech Secure QR. Giao diện trang thanh toán tự động hiển thị thông báo "Thanh toán Thành công!" (kèm hiệu ứng pháo hoa) ngay lập tức mà khách hàng không cần tải lại trang (F5).
- **Gian lận hoặc Sai sót (Luồng Đỏ / Bị chặn):** Trong trường hợp khách hàng cố tình thay đổi số tiền chuyển (chuyển thiếu) trong ứng dụng ngân hàng. Tiền vẫn bị trừ trong tài khoản, nhưng khi Webhook báo về, mô hình AI (Isolation Forest) của hệ thống sẽ lập tức phát hiện sự sai lệch. Giao diện trang web chuyển sang trạng thái cảnh báo màu vàng: **"Giao dịch cần đối soát. Vui lòng chờ CSKH liên hệ!"**.

---

## 6.2. Hướng dẫn dành cho Quản trị viên (Admin)

Quản trị viên là người điều hành, giám sát toàn bộ hoạt động mua bán và ngăn chặn các hành vi gian lận thông qua bảng điều khiển quản trị (Admin Panel).

### 6.2.1. Đăng nhập
- Truy cập vào đường dẫn đăng nhập (`/login`).
- Nhập tài khoản và mật khẩu của Quản trị viên (Ví dụ tài khoản có sẵn: Nguyễn Đình Hòa).

### 6.2.2. Bảng điều khiển tổng quan (Dashboard)
- Sau khi đăng nhập, hệ thống dẫn thẳng vào giao diện tổng quan (`/dashboard`).
- Tại đây hiển thị biểu đồ doanh thu theo thời gian, số lượng giao dịch thành công, và danh sách các giao dịch dòng tiền vào/ra gần nhất. Dashboard giúp Admin dễ dàng nắm bắt được sức khỏe kinh doanh của cửa hàng.

### 6.2.3. Quản lý cảnh báo bằng Trí tuệ nhân tạo (AI Alerts)
- Trong mục **Admin Panel** (`/admin_panel`), hệ thống hiển thị danh sách các **Cảnh báo từ AI**.
- Nếu khách hàng thực hiện thanh toán sai số tiền hoặc giao dịch diễn ra vào những khung giờ bất thường, giao dịch đó lập tức bị dán nhãn đỏ (FLAGGED) và chuyển vào khu vực này kèm theo lý do cụ thể (Ví dụ: "Sai lệch số tiền / Khung giờ dị thường").
- **Tính năng Duyệt thủ công (Human-in-the-loop):** Tính năng này kết hợp sức mạnh của AI và con người. Nếu Admin kiểm tra và xác nhận khách hàng có lý do chính đáng để chuyển thiếu (như được giảm giá ngoài luồng), Admin có thể bấm nút **Duyệt thủ công**. Lúc này giao dịch được chấp nhận, trạng thái được cập nhật thành công xuống cơ sở dữ liệu và hiển thị kết quả về màn hình của người dùng.

### 6.2.4. Quản lý sản phẩm
- Giao diện **Quản lý Sản phẩm** (`/products_manage`) cung cấp các công cụ thiết yếu (Thêm, Xem, Sửa, Xóa) cho danh mục hàng hóa.
- Quản trị viên có thể tải lên hình ảnh, đặt giá bán, số lượng tồn kho và phân loại sản phẩm. Các thay đổi này lập tức được đồng bộ lên trang Cửa hàng.

### 6.2.5. Giám sát Sổ cái Chuỗi khối (Blockchain Ledger)
- Tại trang **Blockchain** (`/blockchain`), Quản trị viên có thể xem lịch sử các khối (block) được sinh ra.
- Toàn bộ mọi giao dịch nảy sinh trong hệ thống (thành công tự động hay duyệt thủ công) đều được mã hóa bằng thuật toán băm **SHA-256** và thêm vào Blockchain cục bộ.
- Khối hiển thị thông tin như `block_index`, `timestamp`, `nonce`, `previous_hash` và `block_hash`. Điều này giúp ban quản trị minh bạch dòng tiền, chống sự can thiệp và giả mạo dữ liệu trực tiếp trong SQL, bảo vệ tính toàn vẹn của sổ cái.

### 6.2.6. Tạo QR Thủ công (QR Generator)
- Trong trường hợp cần nhận tiền ngoài luồng (như khách tới mua trực tiếp tại quầy, hoặc thanh toán công nợ), Admin truy cập tính năng tạo QR (`/qr-generator`).
- Tính năng này cho phép Admin tự nhập số tiền tùy ý và nội dung chuyển khoản để sinh ra một mã QR tức thời đưa cho khách hàng quét thanh toán, tiền vào tài khoản sẽ vẫn được hệ thống ghi nhận tự động. 

## Tổng kết Chương 6
Hệ thống Hutech Secure QR cung cấp một hành trình mua hàng và thanh toán mượt mà cho khách hàng mà không bỏ qua yếu tố bảo mật. Sự hỗ trợ từ mô hình AI đóng vai trò như một màng lọc gian lận, kết hợp với Blockchain đảm bảo tính chống chối bỏ, tạo nên một bộ công cụ quản trị vững chắc, hiệu quả và đáng tin cậy.
