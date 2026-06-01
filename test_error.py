import json
import asyncio
from app.dtos import TransactionInputDTO
from app.repositories import ModelRepository
from app.services import AntiFraudService

def test():
    repo = ModelRepository()
    service = AntiFraudService(repo)
    
    dto = TransactionInputDTO(
        type="TRANSFER",
        amount=100000.0,
        oldbalanceOrg=200000.0,
        newbalanceOrig=100000.0,
        oldbalanceDest=0.0,
        newbalanceDest=100000.0,
        tx_frequency_1m=1,
        login_hour=14,
        is_new_device=0,
        is_vpn_proxy=0,
        failed_login_count=0,
        distance_from_last_login=10.0,
        time_since_last_login=60.0
    )
    
    result = service.analyze_transaction_workflow(dto)
    with open('test_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False)

test()
