# ==========================================================================
# FILE: app/services.py (MODEL - BUSINESS LOGIC LAYER)
# ==========================================================================
import pandas as pd
import numpy as np
import hashlib
import json
import traceback # Thêm thư viện này để bắt và hiển thị lỗi chi tiết
from app.dtos import TransactionInputDTO
from app.repositories import ModelRepository
from app.blockchain_engine import Blockchain

# Khởi tạo instance blockchain (nên để ở mức module để giữ state)
my_blockchain = Blockchain()

class AntiFraudService:
    def __init__(self, repository: ModelRepository):
        # 🟢 LƯU LẠI REPOSITORY ĐỂ GỌI HÀM BLOCKCHAIN Ở TẦNG 5
        self.repo = repository
        
        # Tiếp nhận các thành phần AI được nạp từ lớp Repository hạ tầng
        components = repository.load_all_components()
        self.rf_model = components["rf_model"]
        self.xgb_model = components["xgb_model"]
        self.iso_model = components["iso_model"]
        self.kmeans_model = components["kmeans_model"]
        self.scaler = components["scaler"]
        self.le = components["encoder"]
        self.danger_cluster = components["danger_cluster"]
        
        # Mảng 16 tính năng đầu vào bắt buộc phải đồng bộ với mô hình AI
        self.feature_cols = [
            'amount', 'oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest',
            'type_encoded', 'tx_frequency_1m', 'login_hour', 'is_new_device', 'is_vpn_proxy',
            'failed_login_count', 'distance_from_last_login', 'time_since_last_login',
            'transaction_velocity', 'balance_difference', 'is_night_transaction'
        ]

    def analyze_transaction_workflow(self, dto: TransactionInputDTO) -> dict:
        # Bọc toàn bộ logic trong try-except để bắt lỗi 500 hiển thị thẳng ra Swagger UI
        try:
            reasons = []
            rule_score = 0
            tx_dict = dto.dict()

            # ------------------------------------------------------------------
            # TẦNG 1: ĐỘNG CƠ LUẬT CỐ ĐỊNH PHÂN CẤP TRỌNG SỐ (RULE ENGINE)
            # ------------------------------------------------------------------
            # --- Nhóm A: Luật Nguy cấp (Critical Rules) ---
            sai_lech_so_du = abs((tx_dict['oldbalanceOrg'] - tx_dict['amount']) - tx_dict['newbalanceOrig'])
            if sai_lech_so_du > 10:
                reasons.append("Rule Engine: [Nguy cấp] Phát hiện sai lệch pha số dư toán học (Nghi vấn can thiệp gói tin Payload)")
                rule_score += 40

            if tx_dict['distance_from_last_login'] >= 50 and tx_dict['time_since_last_login'] <= 30:
                reasons.append("Rule Engine: [Nguy cấp] Phát hiện hành vi Impossible Travel (Vị trí địa lý thay đổi bất khả thi)")
                rule_score += 35

            if tx_dict['amount'] >= 50000000 and (2 <= tx_dict['login_hour'] <= 4):
                reasons.append("Rule Engine: [Nguy cấp] Phát hiện giao dịch số tiền lớn phát sinh vào nửa đêm (2h - 4h sáng)")
                rule_score += 30

            # --- Nhóm B: Luật Rủi ro cao (High Risk Rules) ---
            if tx_dict['is_new_device'] == 1 and tx_dict['is_vpn_proxy'] == 1:
                reasons.append("Rule Engine: [Rủi ro cao] Thiết bị lạ truy cập hệ thống cố tình sử dụng VPN/Proxy ẩn danh")
                rule_score += 25

            if tx_dict['tx_frequency_1m'] >= 3:
                reasons.append("Rule Engine: [Rủi ro cao] Tần suất phát lệnh giao dịch vượt ngưỡng (Dấu hiệu Spam/Bot tự động)")
                rule_score += 25

            if tx_dict['type'] == "CASH_OUT" and tx_dict['is_vpn_proxy'] == 1 and tx_dict['amount'] >= 15000000:
                reasons.append("Rule Engine: [Rủi ro cao] Yêu cầu rút tiền mặt giá trị lớn từ xa qua mạng ẩn danh VPN")
                rule_score += 25

            # --- Nhóm C: Luật Cảnh báo hành vi (Medium Risk Rules) ---
            if tx_dict['newbalanceOrig'] == 0 and tx_dict['amount'] >= 10000000:
                reasons.append("Rule Engine: [Cảnh báo] Hành vi rút cạn kiệt số dư tài khoản về bằng 0 (Dấu hiệu tẩu tán tài sản)")
                rule_score += 20

            if tx_dict['is_new_device'] == 1 and tx_dict['amount'] >= 20000000:
                reasons.append("Rule Engine: [Cảnh báo] Thiết bị mới đăng nhập thực hiện ngay giao dịch giá trị lớn")
                rule_score += 20
                
            if tx_dict['failed_login_count'] >= 5:
                reasons.append("Rule Engine: [Cảnh báo] Tài khoản ghi nhận liên tiếp nhiều lần đăng nhập lỗi (Nghi vấn Brute Force)")
                rule_score += 15

            transaction_velocity = tx_dict['amount'] / (tx_dict['tx_frequency_1m'] + 1)
            if transaction_velocity >= 20000000:
                reasons.append("Rule Engine: [Cảnh báo] Vận tốc dịch chuyển dòng tiền trong phiên vượt ngưỡng an toàn")
                rule_score += 15

            # Đặt trần cho bộ lọc luật cứng
            rule_score = min(rule_score, 100)

            # ------------------------------------------------------------------
            # TẦNG 2: KỸ NGHỆ ĐẶC TRƯNG REALTIME (FEATURE ENGINEERING)
            # ------------------------------------------------------------------
            input_df = pd.DataFrame([tx_dict])
            input_df['type_encoded'] = self.le.transform([tx_dict['type']])[0]
            input_df['transaction_velocity'] = transaction_velocity
            input_df['balance_difference'] = abs(tx_dict['oldbalanceOrg'] - tx_dict['newbalanceOrig'])
            input_df['is_night_transaction'] = 1 if 1 <= tx_dict['login_hour'] <= 5 else 0

            # Chuẩn bị ma trận số học đầu vào cho AI
            X_input = input_df[self.feature_cols].astype(float)
            X_input_scaled = self.scaler.transform(X_input)

            # ------------------------------------------------------------------
            # TẦNG 3: TRUY VẾT DỰ ĐOÁN ĐA MÔ HÌNH AI (HYBRID INFERENCE)
            # ------------------------------------------------------------------
            rf_prob = self.rf_model.predict_proba(X_input)[0][1]
            xgb_prob = self.xgb_model.predict_proba(X_input)[0][1]
            iso_pred = self.iso_model.predict(X_input_scaled)[0]
            kmeans_cluster = self.kmeans_model.predict(X_input_scaled)[0]

            if iso_pred == -1:
                reasons.append("Isolation Forest: Mô hình hành vi giao dịch lệch chuẩn nghiêm trọng so với lịch sử hệ thống")
                rule_score += 15

            if kmeans_cluster == self.danger_cluster:
                reasons.append("KMeans: Thuật toán phân cụm xếp dòng tiền hiện tại vào nhóm danh mục hành vi rủi ro")
                rule_score += 10

            if xgb_prob > 0.7 or rf_prob > 0.7:
                reasons.append("Supervised ML: Phân tích cấu trúc dịch chuyển tài sản trùng khớp với hành vi lừa đảo lịch sử")

            # Tính toán điểm Risk Score tổng hợp theo trọng số
            ai_base_score = int(((xgb_prob * 0.5) + (rf_prob * 0.3)) * 100)
            risk_score = min(ai_base_score + rule_score, 100)

            # Phân cấp chỉ số đầu ra
            if risk_score <= 30:
                alert_level, action = "LOW", "ALLOW"
            elif risk_score <= 60:
                alert_level, action = "MEDIUM", "REQUIRE_OTP"
            elif risk_score <= 85:
                alert_level, action = "HIGH", "HOLD_TRANSACTION"
            else:
                alert_level, action = "CRITICAL", "BLOCK_TRANSACTION"

            # ------------------------------------------------------------------
            # TẦNG 4: MÃ HÓA BẤT BIẾN BLOCKCHAIN HASH SHA-256
            # ------------------------------------------------------------------
            tx_string = json.dumps(tx_dict, sort_keys=True)
            blockchain_hash = f"0x{hashlib.sha256(tx_string.encode()).hexdigest()}"
            confidence_score = round(max(rf_prob, xgb_prob) * 100, 2)

            # ------------------------------------------------------------------
            # TẦNG 5: KHẮC LOG LÊN BLOCKCHAIN NỘI BỘ CỦA NHÓM
            # ------------------------------------------------------------------
            data_to_store = {
                "transaction": {
                    "type": tx_dict['type'],
                    "amount": tx_dict['amount'],
                    "old_balance": tx_dict['oldbalanceOrg']
                },
                "hash": blockchain_hash,
                "level": alert_level,
                "score": risk_score,
                "reasons": reasons
            }
            # Lấy hash của khối cuối cùng trong chuỗi nội bộ
            prev_hash = my_blockchain.get_last_block()['hash']
            # Tạo khối mới
            new_block = my_blockchain.create_block(data_to_store, prev_hash)
            
            blockchain_status = f"Khối số {new_block['index']} đã được tạo với Hash: {new_block['hash']}"
            print(f"[BLOCKCHAIN NOI BO]: {blockchain_status}")

            # Trả về kết quả cho API
            return {
                "risk_score": int(risk_score),
                "confidence_score": float(confidence_score),
                "alert_level": str(alert_level),
                "suggested_action": str(action),
                "fraud_reasons": [str(reason) for reason in reasons] if len(reasons) > 0 else ["Giao dịch sạch"],
                "blockchain_hash": str(blockchain_hash),
                "blockchain_internal_log": blockchain_status # Thêm dòng này để show lên giao diện
            }
            
        # NẾU CÓ LỖI, BẮT VÀ IN RA ĐỂ BẮT BỆNH NHANH CHÓNG
        except Exception as e:
            error_details = traceback.format_exc()
            print("[LOI HE THONG]:\n", error_details)
            return {"loi_he_thong": str(e)}