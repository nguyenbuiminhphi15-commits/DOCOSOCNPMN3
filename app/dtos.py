# ==========================================================================
# FILE: app/dtos.py (VIEW SCHEMA / DATA CONTRACT)
# ==========================================================================
from pydantic import BaseModel, Field
from typing import List

class TransactionInputDTO(BaseModel):
    """Định nghĩa 13 trường dữ liệu thô đầu vào do hệ thống gửi sang"""
    type: str = Field(..., description="Loại giao dịch: TRANSFER, CASH_OUT, PAYMENT, DEPOSIT")
    amount: float = Field(..., description="Số tiền giao dịch")
    oldbalanceOrg: float = Field(..., description="Số dư cũ người gửi")
    newbalanceOrig: float = Field(..., description="Số dư mới người gửi")
    oldbalanceDest: float = Field(..., description="Số dư cũ người nhận")
    newbalanceDest: float = Field(..., description="Số dư mới người nhận")
    tx_frequency_1m: int = Field(..., description="Tần suất giao dịch trong 1 phút")
    login_hour: int = Field(..., description="Giờ đăng nhập hệ thống")
    is_new_device: int = Field(..., description="Thiết bị lạ (1) hoặc quen thuộc (0)")
    is_vpn_proxy: int = Field(..., description="Mạng ẩn danh VPN (1) hoặc không (0)")
    failed_login_count: int = Field(..., description="Số lần đăng nhập sai mật khẩu")
    distance_from_last_login: float = Field(..., description="Khoảng cách so với lần đăng nhập trước (km)")
    time_since_last_login: float = Field(..., description="Thời gian cách lần đăng nhập trước (phút)")

class AntiFraudResponseDTO(BaseModel):
    """Định nghĩa cấu trúc dữ liệu JSON phản hồi chuẩn Fintech"""
    risk_score: int
    confidence_score: float
    alert_level: str
    suggested_action: str
    fraud_reasons: List[str]
    blockchain_hash: str
    blockchain_internal_log: str