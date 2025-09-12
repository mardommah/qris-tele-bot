# test_payment_notification.py
import requests
import json

# Contoh penggunaan webhook payment notification
def test_payment_notification():
    """
    Test script untuk mengirim notifikasi pembayaran
    """
    # URL webhook (dalam produksi, ini akan menjadi URL publik server Anda)
    webhook_url = "http://localhost:5000/webhook/payment"
    
    # Data notifikasi pembayaran
    payment_data = {
        "transaction_id": 1,
        "status": "success",
        "amount": "10000"
    }
    
    try:
        # Kirim notifikasi ke webhook
        response = requests.post(
            webhook_url,
            json=payment_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Notifikasi pembayaran berhasil dikirim!")
        else:
            print("❌ Gagal mengirim notifikasi pembayaran")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_payment_notification()