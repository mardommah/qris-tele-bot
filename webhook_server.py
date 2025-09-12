# webhook_server.py
from flask import Flask, request, jsonify
from telegram.ext import ApplicationBuilder
from handlers.webhook import payment_webhook_handler
from config import TELEGRAM_BOT_TOKEN
import asyncio
import threading

app = Flask(__name__)

# Inisialisasi bot application
application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

@app.route('/webhook/payment', methods=['POST'])
def payment_notification():
    """Endpoint untuk menerima notifikasi pembayaran dari payment gateway"""
    try:
        # Dapatkan data dari request
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Ekstrak informasi dari data webhook
        transaction_id = data.get('transaction_id')
        status = data.get('status')  # 'success' atau 'failed'
        amount = data.get('amount')
        
        if not transaction_id or not status:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Jalankan handler notifikasi secara async
        def run_async_handler():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                payment_webhook_handler(transaction_id, status, application)
            )
        
        # Jalankan dalam thread terpisah agar tidak memblokir request
        thread = threading.Thread(target=run_async_handler)
        thread.start()
        
        print(f"Payment notification received: Transaction {transaction_id} status changed to {status}")
        
        return jsonify({'status': 'success', 'message': 'Notification processed'}), 200
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    # Jalankan Flask app di port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)