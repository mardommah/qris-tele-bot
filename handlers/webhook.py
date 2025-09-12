# handlers/webhook.py
from telegram import Update
from telegram.ext import ContextTypes
import json
from database import get_transaction_by_id, update_transaction_status, get_transaction_with_merchant

async def payment_webhook_handler(transaction_id: int, status: str, context):
    """
    Handler untuk mengirim notifikasi pembayaran ke user
    """
    try:
        # Dapatkan detail transaksi
        transaction = get_transaction_with_merchant(transaction_id)
        if not transaction:
            print(f"Transaksi {transaction_id} tidak ditemukan")
            return False
        
        # Update status transaksi
        update_transaction_status(transaction_id, status)
        
        # Kirim notifikasi ke user
        chat_id = transaction[2]  # chat_id dari database
        merchant_name = transaction[9] or "Merchant"
        amount = transaction[4]
        service_fee = transaction[5] or "0"
        total = int(amount) + int(service_fee)
        
        # Buat pesan notifikasi
        if status == 'success':
            message = f"✅ *PEMBAYARAN BERHASIL*\n"
            message += f"🏪 Merchant: {merchant_name}\n"
            message += f"💰 Nominal: Rp {int(amount):,}\n"
            message += f"💳 Biaya Layanan: Rp {int(service_fee):,}\n"
            message += f"📊 Total: Rp {total:,}\n"
            message += f"🆔 ID Transaksi: {transaction_id}\n"
            message += f"\nTerima kasih atas pembayaran Anda!"
        else:
            message = f"❌ *PEMBAYARAN GAGAL*\n"
            message += f"🏪 Merchant: {merchant_name}\n"
            message += f"💰 Nominal: Rp {int(amount):,}\n"
            message += f"💳 Biaya Layanan: Rp {int(service_fee):,}\n"
            message += f"📊 Total: Rp {total:,}\n"
            message += f"🆔 ID Transaksi: {transaction_id}\n"
            message += f"\nSilakan coba kembali atau hubungi admin."
        
        # Kirim notifikasi ke user
        await context.bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode='Markdown'
        )
        
        return True
    except Exception as e:
        print(f"Error sending notification: {str(e)}")
        return False

async def payment_webhook(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler untuk webhook pembayaran (untuk testing)
    Ini akan dipanggil melalui command Telegram
    """
    try:
        if not context.args or len(context.args) < 2:
            await update.message.reply_text("Gunakan: /webhook <transaction_id> <status>")
            return
        
        transaction_id = int(context.args[0])
        status = context.args[1]
        
        success = await payment_webhook_handler(transaction_id, status, context)
        
        if success:
            await update.message.reply_text(f"✅ Notifikasi pembayaran {status} telah dikirim.")
        else:
            await update.message.reply_text("❌ Gagal mengirim notifikasi.")
        
    except ValueError:
        await update.message.reply_text("❌ Transaction ID tidak valid.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")