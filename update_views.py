import os
import re

views_dir = r"c:\Users\HOANG PC\DOANCOSOCNPM\views"
files = ["dashboard.html", "transactions.html", "alerts.html", "reports.html"]

MODAL_CSS = """
        /* Modal Styles */
        .modal {
            display: none; 
            position: fixed; 
            z-index: 1000; 
            left: 0;
            top: 0;
            width: 100%; 
            height: 100%; 
            background-color: rgba(0,0,0,0.7); 
            backdrop-filter: blur(4px);
            align-items: center;
            justify-content: center;
        }
        .modal.show {
            display: flex;
        }
        .modal-content {
            background-color: var(--bg-card);
            padding: 30px;
            border: 1px solid var(--border-color);
            border-radius: 16px;
            width: 700px;
            max-width: 90%;
            max-height: 90vh;
            overflow-y: auto;
            position: relative;
        }
        .close-modal {
            color: var(--text-secondary);
            position: absolute;
            top: 20px;
            right: 20px;
            font-size: 28px;
            cursor: pointer;
            transition: color 0.3s;
        }
        .close-modal:hover {
            color: var(--text-primary);
        }
        .modal-content h3 {
            margin-bottom: 20px;
            font-size: 20px;
        }
        .form-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 20px;
        }
        .form-group-modal label {
            display: block;
            font-size: 13px;
            color: var(--text-secondary);
            margin-bottom: 5px;
        }
        .form-group-modal input, .form-group-modal select {
            width: 100%;
            background-color: var(--bg-input);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            padding: 10px;
            border-radius: 8px;
            outline: none;
            color-scheme: dark;
        }
        .btn-scan-submit {
            width: 100%;
            background-color: var(--accent-blue);
            color: white;
            border: none;
            padding: 14px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: background-color 0.3s;
        }
        .btn-scan-submit:hover {
            background-color: var(--accent-hover);
        }
        .scan-result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 8px;
            background-color: rgba(255,255,255,0.05);
            border: 1px solid var(--border-color);
            display: none;
            font-size: 14px;
            line-height: 1.5;
            white-space: pre-wrap;
        }
        .scan-result.danger { border-color: var(--danger); }
        .scan-result.warning { border-color: var(--warning); }
        .scan-result.success { border-color: var(--success); }
"""

MODAL_HTML = """
    <!-- Modal Quét Giao Dịch -->
    <div id="scanModal" class="modal">
        <div class="modal-content">
            <span class="close-modal">&times;</span>
            <h3>Nhập thông tin giao dịch (Test AI)</h3>
            <form id="scanForm">
                <div class="form-grid">
                    <div class="form-group-modal">
                        <label>Loại giao dịch (type)</label>
                        <select name="type" required>
                            <option value="TRANSFER">TRANSFER</option>
                            <option value="CASH_OUT">CASH_OUT</option>
                            <option value="PAYMENT">PAYMENT</option>
                            <option value="DEPOSIT">DEPOSIT</option>
                        </select>
                    </div>
                    <div class="form-group-modal">
                        <label>Số tiền (amount)</label>
                        <input type="number" step="any" name="amount" value="50000" required>
                    </div>
                    <div class="form-group-modal">
                        <label>Số dư cũ ng.gửi (oldbalanceOrg)</label>
                        <input type="number" step="any" name="oldbalanceOrg" value="100000" required>
                    </div>
                    <div class="form-group-modal">
                        <label>Số dư mới ng.gửi (newbalanceOrig)</label>
                        <input type="number" step="any" name="newbalanceOrig" value="50000" required>
                    </div>
                    <div class="form-group-modal">
                        <label>Số dư cũ ng.nhận (oldbalanceDest)</label>
                        <input type="number" step="any" name="oldbalanceDest" value="20000" required>
                    </div>
                    <div class="form-group-modal">
                        <label>Số dư mới ng.nhận (newbalanceDest)</label>
                        <input type="number" step="any" name="newbalanceDest" value="70000" required>
                    </div>
                    <div class="form-group-modal">
                        <label>Tần suất GD 1 phút (tx_frequency_1m)</label>
                        <input type="number" name="tx_frequency_1m" value="5" required>
                    </div>
                    <div class="form-group-modal">
                        <label>Giờ đăng nhập (login_hour)</label>
                        <input type="number" name="login_hour" value="2" required>
                    </div>
                    <div class="form-group-modal">
                        <label>Thiết bị lạ? (is_new_device: 0/1)</label>
                        <select name="is_new_device" required>
                            <option value="1">1 (Có)</option>
                            <option value="0">0 (Không)</option>
                        </select>
                    </div>
                    <div class="form-group-modal">
                        <label>Dùng VPN/Proxy? (is_vpn_proxy: 0/1)</label>
                        <select name="is_vpn_proxy" required>
                            <option value="1">1 (Có)</option>
                            <option value="0">0 (Không)</option>
                        </select>
                    </div>
                    <div class="form-group-modal">
                        <label>Số lần sai pass (failed_login_count)</label>
                        <input type="number" name="failed_login_count" value="3" required>
                    </div>
                    <div class="form-group-modal">
                        <label>Khoảng cách đăng nhập (km)</label>
                        <input type="number" step="any" name="distance_from_last_login" value="500.5" required>
                    </div>
                    <div class="form-group-modal">
                        <label>Thời gian từ lần chót (phút)</label>
                        <input type="number" step="any" name="time_since_last_login" value="10.0" required>
                    </div>
                </div>
                <button type="submit" class="btn-scan-submit" id="btnSubmitScan">
                    <i class='bx bx-check-shield'></i> Kiểm tra & Đưa vào Blockchain
                </button>
            </form>
            <div id="scanResult" class="scan-result"></div>
        </div>
    </div>
"""

MODAL_JS = """
        // Modal Logic
        const scanModal = document.getElementById('scanModal');
        const closeBtn = document.querySelector('.close-modal');
        const scanForm = document.getElementById('scanForm');
        const scanResult = document.getElementById('scanResult');
        const btnSubmitScan = document.getElementById('btnSubmitScan');

        // Mở modal khi nhấn các nút Quét giao dịch
        document.querySelectorAll('.btn-scan').forEach(btn => {
            btn.addEventListener('click', () => {
                scanModal.classList.add('show');
                scanResult.style.display = 'none';
                scanResult.className = 'scan-result';
            });
        });

        // Đóng modal
        closeBtn.addEventListener('click', () => {
            scanModal.classList.remove('show');
        });
        window.addEventListener('click', (e) => {
            if (e.target === scanModal) {
                scanModal.classList.remove('show');
            }
        });

        // Xử lý submit form
        scanForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(scanForm);
            const data = {};
            for (let [key, value] of formData.entries()) {
                if (['type'].includes(key)) {
                    data[key] = value;
                } else if (['tx_frequency_1m', 'login_hour', 'is_new_device', 'is_vpn_proxy', 'failed_login_count'].includes(key)) {
                    data[key] = parseInt(value);
                } else {
                    data[key] = parseFloat(value);
                }
            }

            try {
                const originalText = btnSubmitScan.innerHTML;
                btnSubmitScan.innerHTML = "<i class='bx bx-loader-alt bx-spin'></i> Đang kiểm tra AI...";
                btnSubmitScan.disabled = true;
                scanResult.style.display = 'none';

                const response = await fetch('/api/ai/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    const result = await response.json();
                    
                    let statusClass = 'success';
                    if (result.alert_level === 'HIGH' || result.alert_level === 'CRITICAL') statusClass = 'danger';
                    else if (result.alert_level === 'MEDIUM') statusClass = 'warning';

                    scanResult.className = `scan-result ${statusClass}`;
                    scanResult.innerHTML = `<strong>KẾT QUẢ QUÉT AI</strong>\\nĐộ rủi ro: ${result.risk_score}/100\\nCảnh báo: ${result.alert_level}\\nHành động: ${result.suggested_action}\\nNguyên nhân: ${result.fraud_reasons.join(", ")}\\n\\n<strong>BLOCKCHAIN</strong>\\nHash: <span style="color:var(--accent-blue)">${result.blockchain_hash}</span>`;
                    scanResult.style.display = 'block';
                } else {
                    alert("Có lỗi xảy ra từ máy chủ khi quét!");
                }
            } catch (error) {
                console.error(error);
                alert("Không thể kết nối đến máy chủ AI.");
            } finally {
                btnSubmitScan.innerHTML = "<i class='bx bx-check-shield'></i> Kiểm tra & Đưa vào Blockchain";
                btnSubmitScan.disabled = false;
            }
        });
"""

for file_name in files:
    path = os.path.join(views_dir, file_name)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    if "/* Modal Styles */" not in content:
        content = content.replace("</style>", MODAL_CSS + "\n    </style>")
    
    if 'id="scanModal"' not in content:
        content = re.sub(r'// Script quét giao dịch \(Gọi API AI\).*?\}\);\n        \}\);', '', content, flags=re.DOTALL)
        content = content.replace("<script>", MODAL_HTML + "\n    <script>\n" + MODAL_JS)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Cập nhật thành công 4 file!")
