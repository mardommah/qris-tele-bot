# webhook_server.py
from flask import Flask, request, jsonify
from telegram import Bot
from telegram.request import HTTPXRequest
import asyncio
import threading
from handlers.webhook import payment_webhook_handler
from config import TELEGRAM_BOT_TOKEN

app = Flask(__name__)

# Inisialisasi bot instance with explicit HTTP backend
request = HTTPXRequest()
bot = Bot(token=TELEGRAM_BOT_TOKEN, request=request)

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
            # Create a simple context object with the bot
            class SimpleContext:
                def __init__(self, bot_instance):
                    self.bot = bot_instance
            
            context = SimpleContext(bot)
            
            # For Python 3.13 compatibility, we need to handle the event loop properly
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(
                    payment_webhook_handler(transaction_id, status, context)
                )
            except Exception as e:
                print(f"Error in async handler: {str(e)}")
            finally:
                loop.close()
        
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