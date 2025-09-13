# handlers/webhook.py
"""Webhook handlers for the QRIS Telegram bot."""

from telegram import Update
from telegram.ext import ContextTypes
import json
from services.database_service import db_service
from services.logging_service import get_logger

logger = get_logger(__name__)

async def payment_webhook_handler(transaction_id: int, status: str, context):
    """
    Handler to send payment notifications to users
    """
    try:
        # Get transaction details
        transaction = db_service.get_transaction_with_merchant(transaction_id)
        if not transaction:
            logger.warning(f"Transaction {transaction_id} not found")
            return False
        
        # Update transaction status
        db_service.update_transaction_status(transaction_id, status)
        
        # Send notification to user
        chat_id = transaction[2]  # chat_id from database
        merchant_name = transaction[9] or "Merchant"
        amount = transaction[4]
        service_fee = transaction[5] or "0"
        total = int(amount) + int(service_fee)
        
        # Create notification message
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
        
        # Send notification to user
        await context.bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode='Markdown'
        )
        
        logger.info(f"Payment notification sent for transaction {transaction_id} with status {status}")
        return True
    except Exception as e:
        logger.error(f"Error sending notification for transaction {transaction_id}: {str(e)}")
        return False

async def payment_webhook(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for payment webhook (for testing)
    This will be called via Telegram command
    """
    try:
        if not context.args or len(context.args) < 2:
            await update.message.reply_text("Gunakan: /webhook <transaction_id> <status>")
            logger.warning(f"User {update.effective_user.id} called webhook without proper arguments")
            return
        
        transaction_id = int(context.args[0])
        status = context.args[1]
        
        success = await payment_webhook_handler(transaction_id, status, context)
        
        if success:
            await update.message.reply_text(f"✅ Notifikasi pembayaran {status} telah dikirim.")
            logger.info(f"User {update.effective_user.id} successfully sent payment notification for transaction {transaction_id}")
        else:
            await update.message.reply_text("❌ Gagal mengirim notifikasi.")
            logger.warning(f"User {update.effective_user.id} failed to send payment notification for transaction {transaction_id}")
        
    except ValueError:
        await update.message.reply_text("❌ Transaction ID tidak valid.")
        logger.warning(f"User {update.effective_user.id} entered invalid transaction ID: {context.args[0]}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")
        logger.error(f"Error in webhook handler for user {update.effective_user.id}: {e}")