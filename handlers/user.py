# handlers/user.py
"""User handlers for the QRIS Telegram bot."""

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from services.database_service import db_service
from services.qris_service import qris_service
from services.telegram_service import telegram_service
from services.logging_service import get_logger

logger = get_logger(__name__)

# State definitions
AMOUNT_INPUT, SERVICE_FEE_INPUT, STOP = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for start command"""
    logger.info(f"User {update.effective_user.id} started the bot")
    
    keyboard = [
        ['Generate QRIS', 'Riwayat Transaksi'],
        ['Bantuan', 'Tutup']
    ]
    reply_markup = telegram_service.create_reply_keyboard(keyboard, resize_keyboard=True)
    
    welcome_text = """
🤖 *Selamat Datang di QRIS Payment Bot*

Fitur yang tersedia:
• 🏦 *Generate QRIS* - Buat QRIS dinamis untuk pembayaran
• 📋 *Riwayat Transaksi* - Lihat semua transaksi Anda
• ℹ️ *Bantuan* - Bantuan penggunaan bot

Silakan pilih menu di bawah ini:
"""

    merchant = db_service.get_merchant_by_owner(update.effective_user.id)
    if not merchant:
        # Jika user bukan admin, beri tahu mereka untuk menghubungi admin
        if not db_service.is_admin(update.effective_user.id):
            logger.info(f"User {update.effective_user.id} does not have a merchant")
            await update.message.reply_text(
                "❌ Anda belum memiliki merchant. Hubungi admin untuk setup merchant.",
                reply_markup=telegram_service.remove_reply_keyboard()
            )
            return ConversationHandler.END
        else:
            # Jika user adalah admin, beri opsi untuk menambah merchant
            logger.info(f"Admin {update.effective_user.id} does not have a merchant")
            admin_keyboard = [
                ['/add_merchant', 'Bantuan'],
                ['Tutup']
            ]
            admin_reply_markup = telegram_service.create_reply_keyboard(admin_keyboard, resize_keyboard=True)
            await update.message.reply_text(
                "👑 Anda adalah admin!\nAnda belum memiliki merchant. Gunakan /add_merchant untuk menambah merchant.",
                reply_markup=admin_reply_markup,
                parse_mode='Markdown'
            )
            return

    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def generate_qris_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate QRIS menu"""
    logger.info(f"User {update.effective_user.id} requested to generate QRIS")
    
    # Create keyboard with stop button
    keyboard = [['Stop']]
    reply_markup = telegram_service.create_reply_keyboard(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    await update.message.reply_text(
        "Masukkan nominal pembayaran (contoh: 10000):",
        reply_markup=reply_markup
    )
    return AMOUNT_INPUT

async def amount_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle amount input"""
    amount = update.message.text.strip()
    logger.info(f"User {update.effective_user.id} entered amount: {amount}")
    
    # Cek jika user menekan tombol Stop
    if amount == "Stop":
        logger.info(f"User {update.effective_user.id} stopped QRIS generation")
        await update.message.reply_text(
            '⏹️ Proses Generate QRIS telah dihentikan.',
            reply_markup=telegram_service.remove_reply_keyboard()
        )
        return ConversationHandler.END
    
    # Validasi amount
    try:
        amount_int = int(amount)
        if amount_int <= 0:
            raise ValueError("Amount harus positif")
    except ValueError:
        logger.warning(f"User {update.effective_user.id} entered invalid amount: {amount}")
        await update.message.reply_text("❌ Nominal tidak valid. Masukkan angka positif.")
        return AMOUNT_INPUT
    
    context.user_data['amount'] = amount
    
    # Tanya apakah ada biaya layanan
    keyboard = [['Ya', 'Tidak']]
    reply_markup = telegram_service.create_reply_keyboard(keyboard, one_time_keyboard=True)
    
    await update.message.reply_text(
        "Apakah ada biaya layanan?",
        reply_markup=reply_markup
    )
    return SERVICE_FEE_INPUT

async def service_fee_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle service fee input"""
    user_response = update.message.text.strip().lower()
    logger.info(f"User {update.effective_user.id} responded to service fee question: {user_response}")
    
    if user_response == 'ya':
        # Create keyboard with stop button
        keyboard = [['Stop']]
        reply_markup = telegram_service.create_reply_keyboard(keyboard, resize_keyboard=True, one_time_keyboard=True)
        
        await update.message.reply_text(
            "Masukkan biaya layanan (contoh: 500):",
            reply_markup=reply_markup
        )
        return SERVICE_FEE_INPUT
    elif user_response == 'tidak':
        # Generate QRIS tanpa biaya layanan
        logger.info(f"User {update.effective_user.id} chose no service fee")
        return await generate_qris_final(update, context, "0")
    else:
        logger.warning(f"User {update.effective_user.id} entered invalid response: {user_response}")
        await update.message.reply_text("❌ Pilihan tidak valid. Pilih 'Ya' atau 'Tidak'.")
        return SERVICE_FEE_INPUT


async def service_fee_amount_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle service fee amount input"""
    user_input = update.message.text.strip()
    logger.info(f"User {update.effective_user.id} entered service fee: {user_input}")
    
    # Cek jika user menekan tombol Stop
    if user_input == "Stop":
        logger.info(f"User {update.effective_user.id} stopped QRIS generation")
        await update.message.reply_text(
            '⏹️ Proses Generate QRIS telah dihentikan.',
            reply_markup=telegram_service.remove_reply_keyboard()
        )
        return ConversationHandler.END
    
    
    # Cek jika user mengklik tombol Generate QRIS Lagi atau Menu Utama
    if user_input == "Generate QRIS Lagi":
        logger.info(f"User {update.effective_user.id} requested to generate QRIS again")
        return await generate_qris_menu(update, context)
    elif user_input == "Menu Utama":
        logger.info(f"User {update.effective_user.id} requested to return to main menu")
        return await start(update, context)
    elif user_input == "Riwayat Transaksi":
        logger.info(f"User {update.effective_user.id} requested transaction history")
        return await history_menu(update, context)
    elif user_input == "Bantuan":
        logger.info(f"User {update.effective_user.id} requested help")
        return await help_menu(update, context)
    elif user_input == "Tutup":
        logger.info(f"User {update.effective_user.id} closed the menu")
        return await close_menu(update, context)
    
    # Validasi service fee
    try:
        service_fee_int = int(user_input)
        if service_fee_int < 0:
            raise ValueError("Service fee tidak boleh negatif")
    except ValueError:
        logger.warning(f"User {update.effective_user.id} entered invalid service fee: {user_input}")
        await update.message.reply_text("❌ Biaya layanan tidak valid. Masukkan angka.")
        return SERVICE_FEE_INPUT
    
    return await generate_qris_final(update, context, user_input)

async def generate_qris_final(update: Update, context: ContextTypes.DEFAULT_TYPE, service_fee: str):
    """Generate final QRIS and send to user"""
    amount = context.user_data.get('amount')
    logger.info(f"User {update.effective_user.id} generating final QRIS with amount: {amount} and service fee: {service_fee}")
    
    if not amount:
        logger.error(f"User {update.effective_user.id} attempted to generate QRIS without amount")
        await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")
        return ConversationHandler.END
    
    merchant = db_service.get_merchant_by_owner(update.effective_user.id)
    if not merchant:
        logger.warning(f"User {update.effective_user.id} does not have a merchant")
        await update.message.reply_text(
            "❌ Anda tidak memiliki merchant. Hubungi admin untuk setup merchant.",
            reply_markup=telegram_service.remove_reply_keyboard()
        )
        return ConversationHandler.END
    
    # Ekstrak data merchant dengan benar
    # Struktur: (id, name, qris_static, qris_image_path, owner_telegram_id, created_at)
    merchant_id = merchant[0]
    merchant_name = merchant[1]
    qris_static = merchant[2]
    
    # Create back button keyboard
    keyboard = [['Generate QRIS Lagi']]
    reply_markup = telegram_service.create_reply_keyboard(keyboard, resize_keyboard=True)
    
    try:
        # Generate QRIS dinamis
        qris_dynamic = qris_service.generate_dynamic_qris(qris_static, amount, service_fee, merchant_id)
        
        # Simpan transaksi
        transaction_id = db_service.add_transaction(
            user_id=update.effective_user.id,
            chat_id=update.effective_chat.id,
            merchant_id=merchant_id,
            amount=amount,
            service_fee=service_fee,
            qris_dynamic=qris_dynamic
        )
        
        # Buat QR Code
        qr_image = qris_service.create_qr_code(qris_dynamic)
        
        # Kirim QR Code
        caption = f"""
🧾 *QRIS DINAMIS*

🏪 Merchant: {merchant_name}
💰 Nominal: Rp {int(amount):,}
💳 Biaya Layanan: Rp {int(service_fee):,}
📊 Total: Rp {int(amount) + int(service_fee):,}

Silakan scan QR Code di atas untuk melakukan pembayaran.
ID Transaksi: {transaction_id}
"""
        await update.message.reply_photo(
            photo=qr_image,
            caption=caption,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        logger.info(f"User {update.effective_user.id} successfully generated QRIS with transaction ID: {transaction_id}")
    except Exception as e:
        logger.error(f"Error generating QRIS for user {update.effective_user.id}: {e}")
        await update.message.reply_text(
            f"❌ Terjadi kesalahan saat Generate QRIS: {e}",
            reply_markup=telegram_service.remove_reply_keyboard()
        )
        return ConversationHandler.END

async def history_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Transaction history menu"""
    logger.info(f"User {update.effective_user.id} requested transaction history")
    
    # Check if user provided a date argument
    date_filter = None
    if context.args:
        date_filter = context.args[0]
    
    # Get transactions based on date filter
    if date_filter:
        transactions = db_service.get_user_transactions_by_date(update.effective_user.id, date_filter)
    else:
        # Show today's transactions by default
        transactions = db_service.get_user_transactions_today(update.effective_user.id)
    
    if not transactions:
        if date_filter:
            logger.info(f"User {update.effective_user.id} has no transaction history for date: {date_filter}")
            await update.message.reply_text(
                f"📭 Anda tidak memiliki riwayat transaksi untuk tanggal {date_filter}.",
                reply_markup=telegram_service.remove_reply_keyboard()
            )
        else:
            logger.info(f"User {update.effective_user.id} has no transaction history for today")
            await update.message.reply_text(
                "📭 Anda belum memiliki riwayat transaksi hari ini.",
                reply_markup=telegram_service.remove_reply_keyboard()
            )
        return
    
    if date_filter:
        history_text = f"*📋 RIWAYAT TRANSAKSI TANGGAL {date_filter}*\n\n"
    else:
        history_text = "*📋 RIWAYAT TRANSAKSI HARI INI*\n\n"
    
    for transaction in transactions[:10]:  # Batasi 10 transaksi terakhir
        _, user_id, chat_id, merchant_id, amount, service_fee, qris_dynamic, status, created_at, merchant_name = transaction
        
        history_text += f"""🆔 ID: {transaction[0]}
🏪 Merchant: {merchant_name or 'NA'}
💰 Nominal: Rp {int(amount):,}
💳 Biaya: Rp {int(service_fee):,}
📊 Total: Rp {int(amount) + int(service_fee):,}
📊 Status: {status.upper()}
🕐 Tanggal: {created_at}

{'-' * 30}
"""
    
    await update.message.reply_text(
        history_text,
        parse_mode='Markdown',
        reply_markup=telegram_service.remove_reply_keyboard()
    )

async def transaction_stats_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Transaction statistics menu"""
    logger.info(f"User {update.effective_user.id} requested transaction statistics")
    
    # Get all user transactions
    transactions = db_service.get_user_transactions(update.effective_user.id)
    
    if not transactions:
        logger.info(f"User {update.effective_user.id} has no transaction history")
        await update.message.reply_text(
            "📭 Anda belum memiliki riwayat transaksi.",
            reply_markup=telegram_service.remove_reply_keyboard()
        )
        return
    
    # Calculate statistics
    total_transactions = len(transactions)
    
    # Calculate totals
    total_amount = 0
    total_service_fee = 0
    successful_transactions = 0
    pending_transactions = 0
    failed_transactions = 0
    
    for transaction in transactions:
        _, user_id, chat_id, merchant_id, amount, service_fee, qris_dynamic, status, created_at, merchant_name = transaction
        total_amount += int(amount)
        total_service_fee += int(service_fee)
        
        if status == "success":
            successful_transactions += 1
        elif status == "pending":
            pending_transactions += 1
        elif status == "failed":
            failed_transactions += 1
    
    # Format statistics text
    stats_text = f"""*📊 STATISTIK TRANSAKSI*

📈 Total Transaksi: {total_transactions}
💰 Total Nominal: Rp {total_amount:,}
💳 Total Biaya Layanan: Rp {total_service_fee:,}
📊 Total Keseluruhan: Rp {total_amount + total_service_fee:,}

✅ Berhasil: {successful_transactions}
⏳ Pending: {pending_transactions}
❌ Gagal: {failed_transactions}

*Status Transaksi:*
✅ Berhasil - Pembayaran berhasil
⏳ Pending - Menunggu pembayaran
❌ Gagal - Pembayaran gagal
"""
    
    await update.message.reply_text(
        stats_text,
        parse_mode='Markdown',
        reply_markup=telegram_service.remove_reply_keyboard()
    )

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help menu"""
    logger.info(f"User {update.effective_user.id} requested help")
    
    help_text = """
🤖 *BANTUAN QRIS PAYMENT BOT*

💳 *Cara Generate QRIS:*
1. Klik menu 'Generate QRIS'
2. Masukkan nominal pembayaran
3. Pilih apakah ada biaya layanan
4. Scan QR Code yang dihasilkan

📋 *Riwayat Transaksi:*
• Lihat semua transaksi Anda
• Status pembayaran akan diperbarui otomatis
• Gunakan /riwayat_transaksi [YYYY-MM-DD] untuk filter tanggal
• Default menampilkan transaksi hari ini

📊 *Statistik Transaksi:*
• Lihat ringkasan transaksi Anda
• Total nominal dan biaya layanan
• Jumlah transaksi berdasarkan status

❓ *Bantuan:*
• Hubungi admin jika ada masalah
• Pastikan nominal dalam rupiah tanpa titikkoma

🛠 *Fitur Admin:*
• Setup merchant QRIS
• Kelola transaksi
• Monitoring pembayaran
"""
    
    await update.message.reply_text(
        help_text,
        parse_mode='Markdown',
        reply_markup=telegram_service.remove_reply_keyboard()
    )

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop QR generation flow"""
    logger.info(f"User {update.effective_user.id} stopped the flow")
    
    await update.message.reply_text(
        '⏹️ Proses Generate QRIS telah dihentikan.',
        reply_markup=telegram_service.remove_reply_keyboard()
    )
    return ConversationHandler.END

async def close_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Close menu handler"""
    logger.info(f"User {update.effective_user.id} closed the menu")
    
    await update.message.reply_text(
        '❌ Menu ditutup.',
        reply_markup=telegram_service.remove_reply_keyboard()
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation"""
    logger.info(f"User {update.effective_user.id} cancelled the conversation")
    
    await update.message.reply_text(
        '❌ Operasi dibatalkan.',
        reply_markup=telegram_service.remove_reply_keyboard()
    )
    return ConversationHandler.END