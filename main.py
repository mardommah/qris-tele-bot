# main.py
import signal
import sys
import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from telegram.request import HTTPXRequest
from handlers.user import *
from handlers.admin import *
from handlers.payment import *
from database import init_db
from config import TELEGRAM_BOT_TOKEN

# Set environment variable to explicitly use asyncio
os.environ['TELEGRAM_BOT_ASYNC_LIB'] = 'asyncio'

def setup_bot():
    """Setup and return the bot application"""
    # Inisialisasi database
    init_db()
    
    # Buat aplikasi bot dengan explicit HTTP backend
    request = HTTPXRequest()
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).request(request).build()
    
    # Handlers untuk user
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_menu))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(CommandHandler("simulate_payment_success", simulate_payment_success))
    application.add_handler(CommandHandler("simulate_payment_failed", simulate_payment_failed))
    
    # Conversation handler untuk generate QRIS
    generate_qris_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^Generate QRIS$'), generate_qris_menu)],
        states={
            AMOUNT_INPUT: [
                MessageHandler(filters.Regex('^Stop$'), stop),
                MessageHandler(filters.TEXT & ~filters.COMMAND, amount_input)
            ],
            SERVICE_FEE_INPUT: [
                MessageHandler(filters.Regex('^Stop$'), stop),
                MessageHandler(filters.Regex('^(Ya|Tidak)$'), service_fee_input),
                MessageHandler(filters.TEXT & ~filters.COMMAND, service_fee_amount_input)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    # Handlers untuk menu
    application.add_handler(generate_qris_conv)
    application.add_handler(MessageHandler(filters.Regex('^Riwayat Transaksi$'), history_menu))
    application.add_handler(MessageHandler(filters.Regex('^Bantuan$'), help_menu))
    
    # Handlers untuk admin
    application.add_handler(CommandHandler("admin", admin_start))
    
    # Conversation handler untuk tambah merchant
    add_merchant_conv = ConversationHandler(
        entry_points=[CommandHandler("add_merchant", add_merchant_start)],
        states={
            MERCHANT_NAME_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, merchant_name_input)],
            MERCHANT_IMAGE_INPUT: [MessageHandler(filters.PHOTO, merchant_image_input)],
            MERCHANT_CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, merchant_confirmation_input)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    # Conversation handler untuk tambah merchant untuk user lain
    add_merchant_for_user_conv = ConversationHandler(
        entry_points=[CommandHandler("add_merchant_for_user", add_merchant_for_user_start)],
        states={
            MERCHANT_USERNAME_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, merchant_user_id_input)],
            MERCHANT_NAME_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, merchant_name_input)],
            MERCHANT_IMAGE_INPUT: [MessageHandler(filters.PHOTO, merchant_image_input)],
            MERCHANT_CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, merchant_confirmation_input)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    # Conversation handler untuk tambah admin
    add_admin_conv = ConversationHandler(
        entry_points=[CommandHandler("add_admin", admin_start)],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_user_id_input)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    # Conversation handler untuk broadcast
    broadcast_conv = ConversationHandler(
        entry_points=[CommandHandler("broadcast", broadcast_start)],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_message_input)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    application.add_handler(add_merchant_conv)
    application.add_handler(add_merchant_for_user_conv)
    application.add_handler(CommandHandler("list_merchants", list_merchants))
    application.add_handler(add_admin_conv)
    application.add_handler(broadcast_conv)
    
    return application

def run_bot(application):
    """Run the bot application"""
    # Handle shutdown gracefully
    def signal_handler(sig, frame):
        print("\nShutting down gracefully...")
        application.stop_running()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Jalankan bot
    print("🤖 QRIS Payment Bot is running...")
    application.run_polling(stop_signals=[])

# For backward compatibility
def main():
    """Main function for backward compatibility"""
    application = setup_bot()
    run_bot(application)

if __name__ == '__main__':
    # This will be called by run_bot.py
    application = setup_bot()
    run_bot(application)