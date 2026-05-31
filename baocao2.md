# BÁO CÁO ĐỒ ÁN (PHẦN NỘI DUNG CHI TIẾT)

## CHƯƠNG 2: CƠ SỞ LÝ THUYẾT VÀ CÔNG NGHỆ ÁP DỤNG

### 2.1 Các công nghệ và ngôn ngữ sử dụng
**2.1.1 Ngôn ngữ lập trình Backend và Frontend**
- **Python:** Được lựa chọn làm ngôn ngữ cốt lõi cho phân hệ Backend nhờ vào hệ sinh thái thư viện phong phú phục vụ khoa học dữ liệu (scikit-learn, pandas) và xử lý logic mạnh mẽ. Python hỗ trợ đắc lực trong việc xử lý đồng thời các tác vụ dự đoán điểm rủi ro bằng AI và giao tiếp với cấu trúc dữ liệu chuỗi khối (Blockchain).
- **HTML5 / CSS3 / JavaScript:** Bộ ba công nghệ tiêu chuẩn được sử dụng tại tầng View nhằm xây dựng giao diện người dùng (Cửa hàng, Giỏ hàng, Admin Dashboard) trực quan, đáp ứng tiêu chuẩn hiển thị thích ứng (Responsive Design) và tương tác thời gian thực (Polling/AJAX) để tự động cập nhật trạng thái hóa đơn.

**2.1.2 Kiến trúc ứng dụng Enterprise MVC**
Hệ thống được tổ chức theo mô hình kiến trúc phân tầng dựa trên MVC (Model-View-Controller) kết hợp Webhook, giúp cô lập các thành phần logic, tăng khả năng mở rộng:
- **Tầng Controllers (Bộ điều khiển):** Xử lý các Route của Flask, tiếp nhận HTTP Request từ phía Client và Webhook từ SePay, kiểm tra dữ liệu đầu vào và điều phối luồng xử lý.
- **Tầng Services (Tầng nghiệp vụ):** Nơi chứa toàn bộ logic xử lý cốt lõi bao gồm: Đối soát số tiền (Amount Matching), gọi Động cơ AI chấm điểm rủi ro (AI Engine), và đóng gói giao dịch để đẩy vào Blockchain.
- **Tầng Data (Tầng truy cập dữ liệu):** Trừu tượng hóa việc truy vấn CSDL SQL Server thông qua các module cấu hình, bảo vệ an toàn chống lỗi SQL Injection.
- **Tầng Views (Giao diện):** Hiển thị dữ liệu trực quan cho người dùng cuối (Mã QR thanh toán) và các quản trị viên (Bảng cảnh báo gian lận) thông qua Jinja2 Template.

  ### 2.2 Trí tuệ nhân tạo (AI Engine) trong phát hiện gian lận
  **2.2.1 Bài toán phát hiện dị thường (Anomaly Detection)**
  Trong thực tế giao dịch tài chính, tỷ lệ giao dịch gian lận thường chỉ chiếm một phần rất nhỏ so với giao dịch hợp lệ. Do đó, thay vì sử dụng các mô hình phân lớp truyền thống dễ bị sai lệch do mất cân bằng dữ liệu, đồ án áp dụng phương pháp Học không giám sát (Unsupervised Learning) để tìm ra các điểm bất thường.

  **2.2.2 Thuật toán Học máy áp dụng**
  - **Isolation Forest (Rừng cô lập):** Đây là thuật toán cốt lõi được sử dụng trong hệ thống. Khác với các thuật toán truyền thống cố gắng mô hình hóa dữ liệu bình thường, Isolation Forest chủ động cô lập các điểm dữ liệu bất thường (Anomalies) bằng cách xây dựng các cây quyết định ngẫu nhiên. Các giao dịch có số tiền quá lớn/quá nhỏ hoặc diễn ra vào khung giờ bất thường (ví dụ: nửa đêm) sẽ bị cô lập rất nhanh và bị gắn nhãn dị thường (-1).

  **2.2.3 Cơ chế phân loại và xử lý rủi ro**
  Đầu ra của mô hình AI kết hợp với bộ lọc quy tắc cứng (Rule-based) sẽ đưa ra phán quyết cuối cùng để xử lý đơn hàng:
  - **Ngưỡng An toàn (Duyệt xanh - PAID):** Khách hàng chuyển khoản khớp 100% số tiền hóa đơn VÀ Mô hình AI trả về kết quả Hợp lệ (1). Hệ thống tự động gạch nợ và thông báo thành công cho khách hàng.
  - **Ngưỡng Nguy hiểm (Cờ vàng đối soát - FLAGGED):** Hệ thống phát hiện Khách hàng chuyển sai số tiền (Mismatch) HOẶC Mô hình AI đánh giá giao dịch là Dị thường (-1). Giao dịch lập tức bị tạm giữ, AI Risk Score được đẩy lên mức rủi ro cao để đưa vào bảng Cảnh báo Đỏ trên Dashboard cho Admin xử lý thủ công (Human-in-the-loop).

### 2.3 Công nghệ Blockchain và An toàn dữ liệu
**2.3.1 Cấu trúc mật mã hình thành Chuỗi khối (Cryptographic Block Structure)**
Mỗi khối (Block) trong hệ thống lưu trữ giao dịch được thiết kế bao gồm các thành phần cơ bản:
- **Block Header:** Chứa số thứ tự khối (Index), mốc thời gian (Timestamp), số định danh dùng một lần (Nonce).
- **Previous Hash:** Chuỗi mã băm SHA-256 của khối ngay trước đó, tạo nên tính chất liên kết chuỗi không thể tách rời.
- **Data:** Toàn bộ thông tin giao dịch (Mã đơn, Số tiền, Loại giao dịch, Quyết định của AI).
- **Current Hash:** Mã băm đại diện cho toàn bộ dữ liệu của khối hiện tại, được tính toán bằng công thức: `Hash = SHA-256(Index + Timestamp + Previous Hash + Data + Nonce)`. Trong đó, `Nonce` là con số ngẫu nhiên được hệ thống liên tục thay đổi trong quá trình "đào" (Mining) để tìm ra mã băm hợp lệ.

**2.3.2 Hàm băm SHA-256 và cơ chế chống giả mạo**
- **Tính một chiều (One-way):** Không thể giải mã ngược từ chuỗi băm ra dữ liệu gốc.
- **Hiệu ứng thác đổ (Avalanche Effect):** Chỉ cần Hacker xâm nhập CSDL và thay đổi một chữ số trong số tiền giao dịch, toàn bộ chuỗi băm đầu ra sẽ thay đổi, làm đứt gãy chuỗi khối và ngay lập tức bị hệ thống phát hiện.

---

## CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG

### 3.1. Sơ đồ Use Case tổng quát
*(Chèn Sơ đồ Use Case đã vẽ bằng Mermaid/PlantUML vào đây)*

### 3.2. Thiết kế Cơ sở dữ liệu
Hệ thống được thiết kế theo mô hình quan hệ (Relational Database) tối ưu hóa cho thương mại điện tử và đối soát tự động, bao gồm 5 bảng dữ liệu cốt lõi:
1. **Users:** Quản lý tài khoản đăng nhập, thông tin ngân hàng thụ hưởng và phân quyền (Admin, Customer).
2. **Store_Orders:** Quản lý đơn hàng mua sắm từ Giỏ hàng, lưu trữ số tiền hóa đơn và trạng thái (PENDING, PAID, FLAGGED).
3. **QR_Links:** Sổ theo dõi các mã QR được tạo thủ công bởi Admin ngoài luồng mua sắm.
4. **Transactions_Ledger:** Sổ cái giao dịch tổng hợp. Đây là bảng quan trọng nhất lưu trữ số tiền thực nhận (actual_amount), mã băm blockchain, và thông tin địa chỉ IP đối soát.
5. **Hutech_Blockchain:** Sổ cái chuỗi khối lưu trữ nguyên bản cấu trúc Blockchain (Index, Nonce, Previous Hash, Block Hash) chống sửa đổi.

  ### 3.3. Thiết kế luồng xử lý (Workflow)
  **Luồng nghiệp vụ Thanh toán & Kiểm duyệt tự động (Auto-Reconciliation & AI Checking)**
  Đây là luồng nghiệp vụ đóng vai trò trái tim của hệ thống. Quá trình xử lý kết hợp giữa Tập luật tĩnh (Rule-based) và Mô hình học máy (AI Engine), sau đó lưu vết lên chuỗi khối (Blockchain).

  - **Bước 1: Tạo đơn & Chờ thanh toán:** Khách hàng chốt giỏ hàng. Hệ thống sinh mã QR động chứa số tiền chuẩn xác và nội dung chuyển khoản duy nhất (VD: `HUTECH_CART_12345`). Trạng thái đơn được lưu là `PENDING`.
  - **Bước 2: Lắng nghe Webhook (SePay API):** Khách hàng dùng App Ngân hàng quét QR. Khi tiền vào tài khoản thực, hệ thống SePay lập tức bắn Webhook về Server. Server thực hiện chuẩn hóa nội dung (Data Normalization) để bóc tách chính xác mã đơn hàng.
  - **Bước 3: Tầng lọc luật tĩnh (Amount Matching):** Hệ thống truy xuất CSDL, đối chiếu `Số tiền thực nhận` từ Webhook với `Số tiền hóa đơn`. Nếu sai lệch (khách chuyển thiếu/dư), lập tức giương cờ vàng báo lỗi.
  - **Bước 4: Phân tích Trí tuệ nhân tạo (AI Engine Layer):** Các giao dịch khớp tiền tiếp tục được đẩy qua mô hình `Isolation Forest`. AI trích xuất đặc trưng (Khung giờ, Số tiền) và chấm điểm rủi ro. Nếu phát hiện dị thường, lập tức giương cờ đỏ.
  - **Bước 5: Ra quyết định (Decision):** 
    - Nếu An toàn tuyệt đối $\rightarrow$ Cập nhật trạng thái `PAID`, giao diện tự động nhảy sang trang Thành công (Ting Ting).
    - Nếu Dị thường/Sai tiền $\rightarrow$ Cập nhật trạng thái `FLAGGED`, giao diện báo "Chờ đối soát".
  - **Bước 6: Lưu vết chuỗi khối (Blockchain Execution):** Bất kể kết quả là PAID hay FLAGGED, thông tin quyết định đều được băm SHA-256 và lưu vào bảng `Hutech_Blockchain` và `Transactions_Ledger` để lưu vết minh bạch, phục vụ kiểm toán.

---

## CHƯƠNG 4: TRIỂN KHAI VÀ ĐÁNH GIÁ MÔ HÌNH

### 4.1. Huấn luyện Mô hình AI với tập dữ liệu PaySim
Để xây dựng Động cơ AI có khả năng nhạy bén với gian lận, đồ án đã tiến hành huấn luyện mô hình dựa trên bộ dữ liệu **PaySim** (PaySim Simulated Mobile Money Transactions). Đây là bộ dữ liệu nổi tiếng được công bố trên Kaggle, chứa hơn 6 triệu dòng giao dịch mô phỏng các hoạt động tài chính thực tế.

**Quá trình Tiền xử lý (Data Preprocessing) và Đặc trưng hóa (Feature Engineering):**
- **Lọc dữ liệu:** Bộ dữ liệu gốc chứa nhiều loại giao dịch (CASH_IN, PAYMENT, DEBIT, TRANSFER, CASH_OUT). Tuy nhiên, các hành vi gian lận (chuyển tiền lừa đảo, đánh cắp tài khoản) chủ yếu xảy ra ở luồng `TRANSFER` và `CASH_OUT`. Do đó, tập dữ liệu được lọc riêng để giảm thiểu nhiễu.
- **Trích xuất đặc trưng thời gian (Time-based Features):** Biến `step` trong PaySim đại diện cho thời gian (1 step = 1 giờ). Hệ thống thực hiện phép chia lấy dư (`step % 24`) để trích xuất ra đặc trưng **Khung giờ giao dịch (Hour)**. Phân tích thăm dò (EDA) cho thấy tỷ lệ gian lận thường tăng vọt vào các khung giờ đêm khuya hoặc rạng sáng.
- **Chuẩn hóa dữ liệu (Scaling):** Đặc trưng **Số tiền (Amount)** có độ lệch chuẩn rất lớn (từ vài nghìn đồng đến hàng tỷ đồng). Để thuật toán Isolation Forest tính toán khoảng cách vector chính xác, biến Amount được chuẩn hóa bằng `StandardScaler`.

**Tiến hành Huấn luyện (Training):**
- Do tỷ lệ gian lận thực tế chỉ chiếm chưa tới 0.2%, bài toán đối mặt với vấn đề mất cân bằng dữ liệu nghiêm trọng. Việc dùng các thuật toán phân lớp (Classification) dễ dẫn đến hiện tượng Overfitting (học vẹt).
- Đồ án quyết định sử dụng **Isolation Forest** (Học máy không giám sát). Thuật toán tiến hành cắt dữ liệu ngẫu nhiên tạo thành các cây (Trees). Các điểm dữ liệu dị thường (ví dụ: chuyển số tiền khổng lồ vào lúc 3 giờ sáng) sẽ cần rất ít nhát cắt để bị "cô lập". 
- Tham số `contamination` (tỷ lệ nhiễu dự kiến) được tinh chỉnh ở mức `0.01` (1%). Sau quá trình huấn luyện, mô hình được trích xuất (Export) ra file `.pkl` để nhúng trực tiếp vào Backend Flask, phục vụ dự đoán thời gian thực.

### 4.2. Đánh giá Khả năng chịu tải và Chống tấn công từ chối dịch vụ (DDoS)
Một hệ thống tự động gạch nợ Real-time bắt buộc phải có tính sẵn sàng cao (High Availability). Nếu Server bị đánh sập, các Webhook từ ngân hàng gửi về sẽ bị thất thoát, dẫn đến mất tiền oan của khách hàng. Do đó, đồ án đã tiến hành kiểm thử sức chịu đựng của hệ thống bằng các công cụ Tấn công Từ chối Dịch vụ (DDoS) khét tiếng:

**a. Thử nghiệm với công cụ HULK (HTTP Unbearable Load King):**
- **Cơ chế:** HULK là công cụ tấn công cực kỳ nguy hiểm ở tầng ứng dụng (Layer 7). Nó liên tục tạo ra hàng loạt các Request HTTP độc nhất (bằng cách làm xáo trộn ngẫu nhiên `User-Agent`, `Referer` và URL parameters) nhằm xuyên thủng các lớp bộ nhớ đệm (Cache) và ép máy chủ (Flask Web Server) phải trực tiếp xử lý tải nặng, dẫn đến vắt kiệt CPU và RAM.
- **Kết quả:** Hệ thống vẫn đứng vững. Nhờ kiến trúc định tuyến qua Reverse Proxy (như Ngrok) kết hợp cơ chế kiểm soát lưu lượng (Rate Limiting) giới hạn số lượng Request trên mỗi IP/phút, các gói tin rác có dấu hiệu bất thường đã bị tự động Drop (thả) ngay từ vòng gửi xe.

**b. Thử nghiệm với công cụ Flood (HTTP/SYN/UDP Flood):**
- **Cơ chế:** Khác với HULK, công cụ Flood tấn công thẳng vào tầng mạng (Layer 4) bằng cách gửi ào ạt hàng ngàn yêu cầu khởi tạo kết nối (SYN) nhưng không bao giờ phản hồi bước cuối (ACK), hoặc dội bom gói tin UDP vô nghĩa nhằm làm tắc nghẽn băng thông của Server.
- **Kết quả:** Mạng lưới bảo vệ vòng ngoài đã hấp thụ phần lớn các đợt dội bom. Các API quan trọng (đặc biệt là API tiếp nhận Webhook thanh toán nội bộ) được cấu hình bộ lọc IP chắt lọc (chỉ cho phép Request đến từ dải IP định trước của đối tác SePay), do đó hacker không thể chèn lưu lượng rác vào luồng đối soát tiền.

### 4.3. Đánh giá giao diện và tính năng thực tế
- **Trải nghiệm mượt mà:** Khách hàng không cần F5 tải lại trang. Nhờ cơ chế Polling ngầm, giao diện Giỏ hàng sẽ tự động nổ pháo hoa và báo "Thành công" ngay giây phút tiền đáp xuống tài khoản ngân hàng.
- **Admin Dashboard Real-time:** Bảng điều khiển dành cho Quản trị viên hiển thị trực quan các giao dịch bị AI gắn cờ đỏ, kèm theo lý do cụ thể (Sai lệch tiền / Khung giờ dị thường / Khả năng bị tấn công), giúp Admin dễ dàng đưa ra quyết định Duyệt tay (Force Approve) hoặc Khóa giao dịch.

---

## CHƯƠNG 5: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

### 5.1. Kết quả đạt được
Hệ thống chứng minh được khả năng vận hành của một Core Thanh toán E-commerce hoàn chỉnh, tích hợp thành công Cổng thanh toán thực tế (SePay) và chạy thời gian thực. Việc áp dụng quy trình nghiệp vụ "Human-in-the-loop" (AI chặn, con người kiểm duyệt) giúp quản lý rủi ro triệt để mà không làm ảnh hưởng trải nghiệm khách hàng hợp pháp.

### 5.2. Hạn chế
Mô hình AI hiện tại (Isolation Forest) đang được huấn luyện dựa trên số lượng đặc trưng (features) cơ bản. Dữ liệu tập huấn luyện chưa bao phủ toàn bộ các biến số phức tạp của ngành tài chính (như vị trí địa lý, mạng lưới thiết bị).

### 5.3. Hướng phát triển
- **Nâng cấp Đặc trưng AI:** Thu thập thêm các Metadata như `IP Geolocation`, `Device Fingerprint`, hoặc tốc độ giao dịch (`Transaction Velocity`) để chống lại các cuộc tấn công tinh vi hơn (như Impossible Travel).
- **Tích hợp Ví điện tử:** Mở rộng cổng thanh toán, hỗ trợ thêm Momo, ZaloPay, VNPay thông qua API chính thức.
- **Kiến trúc Microservices:** Tách biệt Động cơ AI và Hệ thống Blockchain thành các dịch vụ độc lập (Microservices) để tăng khả năng chịu tải khi triển khai lên Cloud.
