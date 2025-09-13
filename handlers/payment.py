# handlers/payment.py
"""Payment handlers for the QRIS Telegram bot."""

from telegram import Update
from telegram.ext import ContextTypes
from services.database_service import db_service
from services.logging_service import get_logger

logger = get_logger(__name__)

async def payment_webhook(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for payment webhook
    This will be called by the payment gateway when payment is successful
    """
    # Implementation of webhook from payment gateway
    # Example data received:
    # {
    #     "transaction_id": 123,
    #     "status": "success",
    #     "amount": 10000
    # }
    
    # For now, we create a manual command for testing
    logger.info("Payment webhook handler called")
    pass

async def simulate_payment_success(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulate successful payment (for testing)"""
    if not context.args:
        await update.message.reply_text("Gunakan: /simulate_payment_success <transaction_id>")
        logger.warning(f"User {update.effective_user.id} called simulate_payment_success without arguments")
        return
    
    try:
        transaction_id = int(context.args[0])
        transaction = db_service.get_transaction_by_id(transaction_id)
        
        if not transaction:
            await update.message.reply_text("❌ Transaksi tidak ditemukan.")
            logger.warning(f"User {update.effective_user.id} tried to simulate payment success for non-existent transaction {transaction_id}")
            return
        
        db_service.update_transaction_status(transaction_id, "success")
        await update.message.reply_text(f"✅ Transaksi {transaction_id} berhasil diperbarui menjadi SUCCESS.")
        logger.info(f"User {update.effective_user.id} simulated payment success for transaction {transaction_id}")
        
    except ValueError:
        await update.message.reply_text("❌ Transaction ID tidak valid.")
        logger.warning(f"User {update.effective_user.id} entered invalid transaction ID: {context.args[0]}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")
        logger.error(f"Error simulating payment success for user {update.effective_user.id}: {e}")

async def simulate_payment_failed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simulate failed payment (for testing)"""
    if not context.args:
        await update.message.reply_text("Gunakan: /simulate_payment_failed <transaction_id>")
        logger.warning(f"User {update.effective_user.id} called simulate_payment_failed without arguments")
        return
    
    try:
        transaction_id = int(context.args[0])
        transaction = db_service.get_transaction_by_id(transaction_id)
        
        if not transaction:
            await update.message.reply_text("❌ Transaksi tidak ditemukan.")
            logger.warning(f"User {update.effective_user.id} tried to simulate payment failure for non-existent transaction {transaction_id}")
            return
        
        db_service.update_transaction_status(transaction_id, "failed")
        await update.message.reply_text(f"❌ Transaksi {transaction_id} berhasil diperbarui menjadi FAILED.")
        logger.info(f"User {update.effective_user.id} simulated payment failure for transaction {transaction_id}")
        
    except ValueError:
        await update.message.reply_text("❌ Transaction ID tidak valid.")
        logger.warning(f"User {update.effective_user.id} entered invalid transaction ID: {context.args[0]}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")
        logger.error(f"Error simulating payment failure for user {update.effective_user.id}: {e}")