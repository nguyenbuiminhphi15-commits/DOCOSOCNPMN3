# ==========================================================================
# FILE: main.py (CORE ENTRYPOINT)
# ==========================================================================
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers.transaction_controller import router as anti_fraud_router

app = FastAPI(
    title="Hệ thống Trợ lý Bảo vệ Tài chính Cá nhân bằng AI & Blockchain",
    description="Kiến trúc phân tầng 3 lớp (MVC) tích hợp Đa mô hình và Luật phòng thủ thực chiến",
    version="3.0.0"
)

# Cấu hình CORS mở cổng kết nối an toàn cho Backend ASP.NET Core
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tích hợp bộ định tuyến Controller vào lõi FastAPI
app.include_router(anti_fraud_router)

# Mount thư mục KYC Wizard
from fastapi.staticfiles import StaticFiles
import os
kyc_path = os.path.join(os.path.dirname(__file__), "..", "aml-kyc-wizard-app")
app.mount("/kyc", StaticFiles(directory=kyc_path, html=True), name="kyc")

from app.services.ai_engine import my_blockchain

@app.get("/blockchain-ledger", tags=["Blockchain Explorer"])
def get_full_ledger():
    """Hiển thị toàn bộ chuỗi khối (sổ cái) nội bộ của hệ thống"""
    return {
        "network_name": "FraudDetection Internal Chain",
        "total_blocks": len(my_blockchain.chain),
        "chain": my_blockchain.chain
    }

from fastapi.responses import HTMLResponse
import os

@app.get("/blockchain", tags=["Blockchain Explorer"], response_class=HTMLResponse)
def get_blockchain_ui():
    """Giao diện người dùng xem Blockchain"""
    html_path = os.path.join(os.path.dirname(__file__), "views", "templates", "blockchain_ui.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/", tags=["Authentication"], response_class=HTMLResponse)
def get_login_ui():
    """Giao diện đăng nhập"""
    html_path = os.path.join(os.path.dirname(__file__), "views", "templates", "login.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/dangki", tags=["Authentication"], response_class=HTMLResponse)
def get_register_ui():
    """Giao diện đăng ký"""
    html_path = os.path.join(os.path.dirname(__file__), "views", "templates", "register.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

# --- DASHBOARD ROUTES ---
@app.get("/dashboard", tags=["Dashboard"], response_class=HTMLResponse)
def get_dashboard_ui():
    """Giao diện Tổng quan Dashboard"""
    html_path = os.path.join(os.path.dirname(__file__), "views", "templates", "dashboard.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/transactions", tags=["Dashboard"], response_class=HTMLResponse)
def get_transactions_ui():
    """Giao diện Danh sách giao dịch"""
    html_path = os.path.join(os.path.dirname(__file__), "views", "templates", "transactions.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/alerts", tags=["Dashboard"], response_class=HTMLResponse)
def get_alerts_ui():
    """Giao diện Cảnh báo"""
    html_path = os.path.join(os.path.dirname(__file__), "views", "templates", "alerts.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/reports", tags=["Dashboard"], response_class=HTMLResponse)
def get_reports_ui():
    """Giao diện Báo cáo"""
    html_path = os.path.join(os.path.dirname(__file__), "views", "templates", "reports.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)