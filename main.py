# main.py
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from handlers.user import *
from handlers.admin import *
from handlers.payment import *
from database import init_db
from config import TELEGRAM_BOT_TOKEN

def main():
    # Inisialisasi database
    init_db()
    
    # Buat aplikasi bot
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
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
            AMOUNT_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, amount_input)],
            SERVICE_FEE_INPUT: [
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
            MERCHANT_QRIS_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, merchant_qris_input)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    # Conversation handler untuk tambah admin
    add_admin_conv = ConversationHandler(
        entry_points=[CommandHandler("add_admin", add_admin_start)],
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
    application.add_handler(CommandHandler("list_merchants", list_merchants))
    application.add_handler(add_admin_conv)
    application.add_handler(broadcast_conv)
    
    # Jalankan bot
    print("🤖 QRIS Payment Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()