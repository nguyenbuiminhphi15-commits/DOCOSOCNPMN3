# ==========================================================================
# FILE: app/repositories.py (CẬP NHẬT ĐOẠN KẾT NỐI BLOCKCHAIN VÀ LOAD MODEL)
# ==========================================================================
import joblib
import json
import os
from web3 import Web3

class ModelRepository:
    def __init__(self):
        self.model_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'models_data')
        
        # 1. Cấu hình cổng kết nối mạng Ganache của bạn
        self.w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
        
        # 2. ĐỊA CHỈ CONTRACT: Dán chuỗi kí tự bạn vừa copy ở Phần 1 vào đây
        self.contract_address = "0xBAc6776b97C7dB85D9639207038dBbc6761A639B" # <--- Thay bằng địa chỉ thật của bạn
        
        # 3. CHUỖI ABI: Đây là chuỗi ABI rút gọn và chuẩn hóa từ Phần 2 để Python đọc trực tiếp
        self.contract_abi = json.loads('[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"string","name":"blockHash","type":"string"},{"indexed":false,"internalType":"string","name":"alertLevel","type":"string"},{"indexed":false,"internalType":"uint256","name":"riskScore","type":"uint256"}],"name":"AuditRecorded","type":"event"},{"inputs":[{"internalType":"string","name":"_blockHash","type":"string"},{"internalType":"string","name":"_alertLevel","type":"string"},{"internalType":"uint256","name":"_riskScore","type":"uint256"}],"name":"recordFraudLog","type":"function","outputs":[],"stateMutability":"nonpayable","type":"function"}]')

    def load_all_components(self):
        with open(os.path.join(self.model_dir, 'kmeans_config.json'), 'r') as f:
            kmeans_config = json.load(f)

        return {
            "rf_model": joblib.load(os.path.join(self.model_dir, 'random_forest_model.joblib')),
            "xgb_model": joblib.load(os.path.join(self.model_dir, 'xgboost_model.joblib')),
            "iso_model": joblib.load(os.path.join(self.model_dir, 'isolation_forest_model.joblib')),
            "kmeans_model": joblib.load(os.path.join(self.model_dir, 'kmeans_model.joblib')),
            "scaler": joblib.load(os.path.join(self.model_dir, 'global_scaler.joblib')),
            "encoder": joblib.load(os.path.join(self.model_dir, 'global_encoder.joblib')),
            "danger_cluster": kmeans_config.get("danger_cluster", 1)
        }

    def push_to_blockchain(self, block_hash: str, alert_level: str, risk_score: int):
        try:
            if not self.w3.is_connected():
                return "Lỗi: Không thể kết nối với mạng Ganache (Blockchain)"
            
            contract = self.w3.eth.contract(address=self.contract_address, abi=self.contract_abi)
            
            # Sử dụng tài khoản đầu tiên trong Ganache làm tài khoản gửi giao dịch
            account = self.w3.eth.accounts[0]
            
            tx_hash = contract.functions.recordFraudLog(
                block_hash, 
                alert_level, 
                risk_score
            ).transact({'from': account})
            
            # Đợi giao dịch được đào thành công
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return f"Thành công ghi block (Gas used: {tx_receipt.gasUsed})"
            
        except Exception as e:
            return f"Lỗi khi tương tác Blockchain: {str(e)}"