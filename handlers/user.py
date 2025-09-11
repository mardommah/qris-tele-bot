# handlers/user.py
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from database import get_user_transactions, get_default_merchant, add_transaction
from qris_generator import generate_dynamic_qris, create_qr_code

# State definitions
AMOUNT_INPUT, SERVICE_FEE_INPUT = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /start"""
    keyboard = [
        ['Generate QRIS', 'Riwayat Transaksi'],
        ['Bantuan']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_text = """
🤖 *Selamat Datang di QRIS Payment Bot*

Fitur yang tersedia:
• 🏦 *Generate QRIS* - Buat QRIS dinamis untuk pembayaran
• 📋 *Riwayat Transaksi* - Lihat semua transaksi Anda
• ℹ️ *Bantuan* - Bantuan penggunaan bot

Silakan pilih menu di bawah ini:
"""
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def generate_qris_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menu Generate QRIS"""
    await update.message.reply_text(
        "Masukkan nominal pembayaran (contoh: 10000):",
        reply_markup=ReplyKeyboardRemove()
    )
    return AMOUNT_INPUT

async def amount_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Input nominal pembayaran"""
    amount = update.message.text.strip()
    
    # Validasi amount
    try:
        amount_int = int(amount)
        if amount_int <= 0:
            raise ValueError("Amount harus positif")
    except ValueError:
        await update.message.reply_text("❌ Nominal tidak valid. Masukkan angka positif.")
        return AMOUNT_INPUT
    
    context.user_data['amount'] = amount
    
    # Tanya apakah ada biaya layanan
    keyboard = [['Ya', 'Tidak']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    
    await update.message.reply_text(
        "Apakah ada biaya layanan?",
        reply_markup=reply_markup
    )
    return SERVICE_FEE_INPUT

async def service_fee_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Input biaya layanan"""
    user_response = update.message.text.strip().lower()
    
    if user_response == 'ya':
        await update.message.reply_text(
            "Masukkan biaya layanan (contoh: 500):",
            reply_markup=ReplyKeyboardRemove()
        )
        return SERVICE_FEE_INPUT
    elif user_response == 'tidak':
        # Generate QRIS tanpa biaya layanan
        return await generate_qris_final(update, context, "0")
    else:
        await update.message.reply_text("❌ Pilihan tidak valid. Pilih 'Ya' atau 'Tidak'.")
        return SERVICE_FEE_INPUT

async def service_fee_amount_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Input jumlah biaya layanan"""
    service_fee = update.message.text.strip()
    
    # Validasi service fee
    try:
        service_fee_int = int(service_fee)
        if service_fee_int < 0:
            raise ValueError("Service fee tidak boleh negatif")
    except ValueError:
        await update.message.reply_text("❌ Biaya layanan tidak valid. Masukkan angka.")
        return SERVICE_FEE_INPUT
    
    return await generate_qris_final(update, context, service_fee)

async def generate_qris_final(update: Update, context: ContextTypes.DEFAULT_TYPE, service_fee: str):
    """Generate QRIS final dan kirim ke user"""
    amount = context.user_data.get('amount')
    
    if not amount:
        await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")
        return ConversationHandler.END
    
    # Dapatkan merchant default
    merchant = get_default_merchant()
    if not merchant:
        await update.message.reply_text(
            "❌ Belum ada merchant yang terdaftar. Hubungi admin untuk setup merchant.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    merchant_id, merchant_name, qris_static, _ = merchant
    
    try:
        # Generate QRIS dinamis
        qris_dynamic = generate_dynamic_qris(qris_static, amount, service_fee, merchant_id)
        
        # Simpan transaksi
        transaction_id = add_transaction(
            user_id=update.effective_user.id,
            merchant_id=merchant_id,
            amount=amount,
            service_fee=service_fee,
            qris_dynamic=qris_dynamic
        )
        
        # Buat QR Code
        qr_image = create_qr_code(qris_dynamic)
        
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
            reply_markup=ReplyKeyboardRemove()
        )
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ Terjadi kesalahan saat generate QRIS: {str(e)}",
            reply_markup=ReplyKeyboardRemove()
        )
    
    return ConversationHandler.END

async def history_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menu Riwayat Transaksi"""
    transactions = get_user_transactions(update.effective_user.id)
    
    if not transactions:
        await update.message.reply_text(
            "📭 Anda belum memiliki riwayat transaksi.",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    
    history_text = "*📋 RIWAYAT TRANSAKSI*\n\n"
    
    for transaction in transactions[:10]:  # Batasi 10 transaksi terakhir
        _, user_id, merchant_id, amount, service_fee, _, status, created_at, merchant_name = transaction
        
        history_text += f"""
🆔 ID: {transaction[0]}
🏪 Merchant: {merchant_name or 'N/A'}
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
        reply_markup=ReplyKeyboardRemove()
    )

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menu Bantuan"""
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

❓ *Bantuan:*
• Hubungi admin jika ada masalah
• Pastikan nominal dalam rupiah tanpa titik/koma

🛠 *Fitur Admin:*
• Setup merchant QRIS
• Kelola transaksi
• Monitoring pembayaran
"""
    
    await update.message.reply_text(
        help_text,
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardRemove()
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation"""
    await update.message.reply_text(
        '❌ Operasi dibatalkan.',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END