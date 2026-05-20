# ==========================================================================
# FILE: app/controllers.py (CONTROLLER LAYER)
# ==========================================================================
from fastapi import APIRouter, HTTPException, Depends
from app.dtos import TransactionInputDTO, AntiFraudResponseDTO
from app.repositories import ModelRepository
from app.services import AntiFraudService

router = APIRouter(prefix="/api/ai", tags=["Hệ thống lõi phân tích rủi ro AI"])

# Khởi tạo Dependency Injection để quản lý luồng dữ liệu sạch giữa các lớp
def get_anti_fraud_service() -> AntiFraudService:
    repo = ModelRepository()
    return AntiFraudService(repo)

@router.post("/analyze", response_model=AntiFraudResponseDTO)
def analyze_transaction_endpoint(tx_input: TransactionInputDTO, service: AntiFraudService = Depends(get_anti_fraud_service)):
    """Endpoint HTTP POST tiếp nhận yêu cầu chấm điểm rủi ro tài chính trực tiếp"""
    try:
        # Chuyển giao toàn bộ trách nhiệm xử lý thuật toán xuống lớp Service nghiệp vụ
        result = service.analyze_transaction_workflow(tx_input)
        if "loi_he_thong" in result:
            raise HTTPException(status_code=500, detail=result["loi_he_thong"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống tại lớp Controller: {str(e)}")