# handlers/payment.py
from telegram import Update
from telegram.ext import ContextTypes
from database import update_transaction_status, get_transaction_by_id

async def payment_webhook(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler untuk webhook pembayaran
    Ini akan dipanggil oleh payment gateway saat pembayaran berhasil
    """
    # Implementasi webhook dari payment gateway
    # Contoh data yang diterima:
    # {
    #     "transaction_id": 123,
    #     "status": "success",
    #     "amount": 10000
    # }
    
    # Untuk sementara, kita buat command manual untuk testing
    pass

async def simulate_payment_success(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulasi pembayaran berhasil (untuk testing)"""
    if not context.args:
        await update.message.reply_text("Gunakan: /simulate_payment_success <transaction_id>")
        return
    
    try:
        transaction_id = int(context.args[0])
        transaction = get_transaction_by_id(transaction_id)
        
        if not transaction:
            await update.message.reply_text("❌ Transaksi tidak ditemukan.")
            return
        
        update_transaction_status(transaction_id, "success")
        await update.message.reply_text(f"✅ Transaksi {transaction_id} berhasil diperbarui menjadi SUCCESS.")
        
    except ValueError:
        await update.message.reply_text("❌ Transaction ID tidak valid.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def simulate_payment_failed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulasi pembayaran gagal (untuk testing)"""
    if not context.args:
        await update.message.reply_text("Gunakan: /simulate_payment_failed <transaction_id>")
        return
    
    try:
        transaction_id = int(context.args[0])
        transaction = get_transaction_by_id(transaction_id)
        
        if not transaction:
            await update.message.reply_text("❌ Transaksi tidak ditemukan.")
            return
        
        update_transaction_status(transaction_id, "failed")
        await update.message.reply_text(f"❌ Transaksi {transaction_id} berhasil diperbarui menjadi FAILED.")
        
    except ValueError:
        await update.message.reply_text("❌ Transaction ID tidak valid.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")