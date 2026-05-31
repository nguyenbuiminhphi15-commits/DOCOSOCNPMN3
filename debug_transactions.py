import sys
sys.path.append('c:\\Users\\HOANG PC\\Source\\Repos\\Hutech_SecureQR')
from flask import Flask, render_template, session
from app import app, db
import os

app.config['SERVER_NAME'] = 'localhost:5000'
with app.app_context():
    with app.test_request_context('/transactions'):
        # Mock the session
        session['user_id'] = 1
        session['role'] = 'ADMIN'
        
        # We need to run the transactions() route logic
        conn = db.get_connection()
        user_bank = None
        txs = []
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT bank_code, bank_account, full_name FROM Users WHERE user_id = ?", (session['user_id'],))
            row = cursor.fetchone()
            if row and row[1]:
                user_bank = {
                    'bank_code': row[0],
                    'bank_account': row[1],
                    'full_name': row[2] or 'Chưa cập nhật'
                }
            
            query = """
                SELECT 
                    TL.tx_id, 
                    TL.created_at, 
                    U.bank_account, 
                    U.bank_code,
                    QL.account_no, 
                    TL.actual_amount, 
                    QL.description,
                    TL.block_hash,
                    TL.status
                FROM Transactions_Ledger TL
                JOIN QR_Links QL ON TL.qr_id = QL.qr_id
                JOIN Users U ON QL.user_id = U.user_id
                WHERE U.user_id = ?
                ORDER BY TL.created_at DESC
            """
            cursor.execute(query, (session['user_id'],))
            for tx_row in cursor.fetchall():
                txs.append({
                    "id": tx_row[0],
                    "created_at": tx_row[1].strftime("%d/%m/%Y %H:%M:%S") if tx_row[1] else "",
                    "bank_account": tx_row[2] or "",
                    "bank_code": tx_row[3] or "",
                    "virtual_account": tx_row[4] or "",
                    "amount": tx_row[5] or 0,
                    "description": tx_row[6] or "",
                    "reference": tx_row[7] or "",
                    "status": tx_row[8] or ""
                })
        
        # Render the template
        html = render_template('transactions.html', user_bank=user_bank, transactions=txs)
        
        # Write to file so we can inspect it
        with open('debug_transactions.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("Wrote debug_transactions.html with", len(txs), "transactions.")
