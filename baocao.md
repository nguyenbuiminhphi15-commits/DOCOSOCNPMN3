# BÁO CÁO ĐỒ ÁN: HỆ THỐNG THANH TOÁN QR SECURE KẾT HỢP TRÍ TUỆ NHÂN TẠO (AI) VÀ BLOCKCHAIN

## Phần Mở Đầu

**1. Lý do chọn đề tài:**
Trong bối cảnh thanh toán không tiền mặt bùng nổ mạnh mẽ tại Việt Nam, các cửa hàng và doanh nghiệp phải đối mặt với nhiều rủi ro gian lận (chuyển thiếu tiền, làm giả bill, test thẻ) cùng với gánh nặng đối soát thủ công gây lãng phí nguồn lực. Do đó, một hệ thống thanh toán thông minh có khả năng tự động hóa và tự phòng vệ là cực kỳ cấp thiết.

**2. Mục tiêu đề tài:**
Xây dựng hệ thống tự động hóa gạch nợ Real-time thông qua mã QR động, đồng thời tích hợp mô hình Machine Learning để phát hiện gian lận và công nghệ Blockchain để đảm bảo tính toàn vẹn của sổ cái kế toán.

---

## Chương 1: Cơ sở Lý thuyết & Công nghệ áp dụng

**1.1. Kiến trúc phần mềm (Backend & Frontend):**
- Ngôn ngữ & Framework: Python Flask, Jinja2 template engine.
- Giao diện: HTML5, CSS3, JavaScript (Fetch API cho polling realtime), Bootstrap.
- Cơ sở dữ liệu: SQL Server.

**1.2. Fintech API (Cổng thanh toán):**
- Sử dụng công nghệ Tài khoản ảo (Virtual Account) kết hợp với cơ chế Webhook của nền tảng **SePay** để lắng nghe dòng tiền vào tài khoản ngân hàng thực tế (Napas 247).

**1.3. Trí tuệ nhân tạo (AI - Anomaly Detection):**
- Ứng dụng thuật toán học máy không giám sát **Isolation Forest** để nhận diện dữ liệu bất thường (Anomaly Detection).
- AI phân tích các đặc trưng (features) như: Số tiền giao dịch, Khung giờ giao dịch để tự động đưa ra phán quyết (Business Verdict) có cho phép gạch nợ hay không.

**1.4. Công nghệ Chuỗi khối (Blockchain Ledger):**
- Lưu trữ mọi giao dịch vào một sổ cái phi tập trung nội bộ (`Hutech_Blockchain`).
- Sử dụng thuật toán băm **SHA-256**, **Nonce** và cơ chế **Proof of Work** nhẹ để đóng khối (mine block). Đảm bảo mọi giao dịch đã ghi nhận không thể bị chỉnh sửa hay chối cãi (Immutable).

---

## Chương 2: Phân tích & Thiết kế Hệ thống

**2.1. Thiết kế Kiến trúc Tổng thể:**
Hệ thống vận hành theo mô hình Client - Server - Third Party (SePay API). Đảm bảo luồng xử lý phi đồng bộ, Frontend không cần can thiệp vào quá trình đối soát tiền.

**2.2. Sơ đồ Use Case Tổng Quan:**
Sơ đồ dưới đây tập trung trả lời 2 câu hỏi cốt lõi: **Ai (Actor)** đang tương tác và **Làm gì (Use Case)** trong hệ thống. Hệ thống có sự tham gia của con người (Khách hàng, Admin) và các Tác nhân tự động (SePay, AI, Blockchain).

```mermaid
flowchart LR
    %% Định nghĩa các Actor (Tác nhân)
    Customer(("\n🧍 Khách hàng\n"))
    Admin(("\n👨‍💼 Quản trị viên\n"))
    SePay(("\n🏦 Đối tác SePay\n"))
    AI(("\n🤖 Hệ thống AI\n"))
    Blockchain(("\n⛓️ Chuỗi Blockchain\n"))

    %% Định nghĩa Boundary Hệ thống và các Use Case (Hành động)
    subgraph Hutech Secure QR System
        direction TB
        
        %% Use cases của Khách hàng
        UC1([Thêm vào giỏ hàng & Chốt đơn])
        UC2([Quét mã QR thanh toán])
        UC3([Nhận thông báo tự động (Ting Ting)])
        
        %% Use cases của Admin
        UC4([Quản lý tài khoản người dùng])
        UC5([Tạo mã QR nhận tiền thủ công])
        UC6([Theo dõi luồng tiền trên Sổ cái])
        UC7([Duyệt/Mở khóa các đơn bị gắn cờ])
        UC8([Giám sát các khối Blockchain])

        %% Use cases của SePay
        UC9([Bắn Webhook báo biến động số dư])
        
        %% Use cases của AI & Blockchain
        UC10([Quét dị thường số tiền & khung giờ])
        UC11([Đóng khối lưu vết chống chối cãi])
    end

    %% Kết nối Actor với Use Case
    Customer --- UC1
    Customer --- UC2
    Customer --- UC3

    Admin --- UC4
    Admin --- UC5
    Admin --- UC6
    Admin --- UC7
    Admin --- UC8

    SePay -.->|<<include>>| UC9
    UC9 -.->|<<include>>| UC10
    AI -.->|Thực thi| UC10
    
    UC10 -.->|<<include>>| UC11
    Blockchain -.->|Thực thi| UC11
    
    UC7 -.->|<<extend>>| UC10
```

**2.3. Sơ đồ Luồng dữ liệu (Flowchart) - Cốt lõi hệ thống:**
1. Khách hàng chốt đơn hàng trên Web.
2. Server tạo Mã đơn hàng (`HUTECH_CART_...`) và sinh ra QR Code tĩnh động chứa nội dung và số tiền chuẩn xác.
3. Dữ liệu trạng thái tạm thời (`PENDING`) được ghi vào `Store_Orders` và `Transactions_Ledger`.
4. Khách quét QR chuyển khoản qua App Ngân hàng. Ngân hàng chuyển tiền qua hệ thống Napas.
5. SePay ghi nhận biến động số dư và đẩy **Webhook** về Server.
6. Server chuẩn hóa nội dung (Data Normalization), ghép nối ID và ném dữ liệu vào **Mô hình AI kiểm duyệt**.
7. Cùng lúc, Server đối soát số tiền (Amount Matching) giữa `transfer_amount` và `order_amount`.
8. Hệ thống ra quyết định cập nhật trạng thái `PAID` (Duyệt xanh) hoặc `FLAGGED` (Cờ vàng đối soát).
9. Mọi quyết định đều được Đóng khối (Mine Block) và cập nhật mã băm vào Sổ cái `Transactions_Ledger`.
10. Frontend Polling nhận tín hiệu và hiển thị cho người dùng.

**2.4. Thiết kế Cơ sở dữ liệu (ERD):**
Các bảng cốt lõi bao gồm:
- `Users`: Quản lý tài khoản (Admin, Customer).
- `Store_Orders`: Sổ theo dõi đơn đặt hàng từ trang mua sắm (Storefront).
- `QR_Links`: Sổ theo dõi các mã QR được tạo thủ công bởi Admin.
- `Transactions_Ledger`: Sổ cái tài chính tổng hợp (Nơi hội tụ mọi luồng tiền).
- `Hutech_Blockchain`: Sổ cái chuỗi khối (Lưu trữ block_hash, previous_hash, nonce chống sửa đổi).

---

## Chương 3: Triển khai & Đánh giá kết quả

**3.1. Kết quả giao diện (UI/UX):**
- Màn hình Cửa hàng và Giỏ hàng thân thiện, tự động sinh QR Code và đếm ngược thời gian (10 phút).
- Hệ thống lắng nghe (Short-polling) mượt mà, tự động chuyển trang khi thanh toán hoàn tất.
- Admin Panel trực quan, hiển thị Real-time cảnh báo AI và số liệu Blockchain.

**3.2. Demo tính năng bảo mật AI đa lớp:**
- **Trường hợp 1 (Giao dịch Hợp lệ - Duyệt Xanh):** Khách hàng chuyển đúng số tiền của hóa đơn (Ví dụ: 150.000đ). AI kiểm tra khung giờ hợp lý và xác nhận khớp tiền tuyệt đối -> Hệ thống tự động gạch nợ, nổ pháo hoa ăn mừng trên màn hình khách.
- **Trường hợp 2 (Giao dịch Dị thường - Đánh Cờ Vàng):** Khách hàng hoặc Hacker cố tình sửa số tiền (chỉ chuyển 2.000đ) để qua mặt hệ thống. AI phát hiện sai lệch số tiền (Amount Mismatch) hoặc hành vi khác thường (khung giờ đêm khuya) -> Webhook giương cờ đỏ (FLAGGED), đóng khối rủi ro vào Blockchain và cảnh báo Real-time trên Dashboard của Admin. Khách hàng nhận được thông báo "Vui lòng chờ đối soát".

**3.3. Demo Công nghệ Blockchain:**
Hệ thống chứng minh được năng lực tự động đào khối trong Terminal: `💎 Đào thành công! Nonce: 33890 | Hash: 0000289...`. Khớp nối hoàn hảo với giao diện dữ liệu khối trên trang quản trị Admin.

---

## Chương 4: Kết luận & Hướng phát triển

**4.1. Ưu điểm nổi bật:**
- Tự động hóa quá trình đối soát 100%, giảm thiểu sức lao động của con người.
- Kiến trúc bảo mật đa tầng: Kiểm tra dữ liệu tĩnh (SQL), Bảo vệ động (AI Anomaly Detection), và Chống chối cãi (Blockchain Immutable Ledger).
- Cơ chế *Human-in-the-loop*: AI làm nhiệm vụ cảnh báo, quyết định xử lý cuối cùng đối với các giao dịch nghi vấn vẫn nằm trong tay Admin, đảm bảo không khóa nhầm khách hàng thật.

**4.2. Hướng phát triển trong tương lai:**
- Nâng cấp mô hình Học máy (Machine Learning) đa chiều hơn bằng cách đưa thêm các tham số (Features) như: Vị trí địa lý (IP Geolocation), Thông tin thiết bị (Device Fingerprint), hay Nhận diện OCR các hình ảnh biên lai.
- Tích hợp thêm đa dạng cổng thanh toán ví điện tử (Momo, ZaloPay, VNPay).
- Triển khai kiến trúc Microservices để tách biệt Module AI và Module Blockchain thành các service độc lập.
