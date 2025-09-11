# handlers/admin.py
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from database import add_merchant, get_merchants, add_admin, is_admin
from config import ADMIN_USER_ID

# State definitions
MERCHANT_NAME_INPUT, MERCHANT_QRIS_INPUT = range(2)

async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menu Admin"""
    user_id = update.effective_user.id
    
    # Cek apakah user adalah admin
    if user_id != ADMIN_USER_ID and not is_admin(user_id):
        await update.message.reply_text("❌ Akses ditolak. Anda bukan admin.")
        return
    
    admin_text = """
👑 *ADMIN MENU*

🔧 *Fitur Admin:*
• /add_merchant - Tambah merchant QRIS
• /list_merchants - Lihat semua merchant
• /add_admin - Tambah admin baru
• /broadcast - Kirim pesan ke semua user

Gunakan command di atas untuk mengakses fitur admin.
"""
    
    await update.message.reply_text(admin_text, parse_mode='Markdown')

async def add_merchant_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mulai tambah merchant"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_USER_ID and not is_admin(user_id):
        await update.message.reply_text("❌ Akses ditolak.")
        return ConversationHandler.END
    
    await update.message.reply_text("Masukkan nama merchant:")
    return MERCHANT_NAME_INPUT

async def merchant_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Input nama merchant"""
    name = update.message.text.strip()
    context.user_data['merchant_name'] = name
    
    await update.message.reply_text("Masukkan QRIS statis merchant:")
    return MERCHANT_QRIS_INPUT

async def merchant_qris_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Input QRIS statis merchant"""
    qris_static = update.message.text.strip()
    name = context.user_data.get('merchant_name')
    
    if not name or not qris_static:
        await update.message.reply_text("❌ Data tidak lengkap.")
        return ConversationHandler.END
    
    try:
        merchant_id = add_merchant(name, qris_static)
        await update.message.reply_text(f"✅ Merchant '{name}' berhasil ditambahkan dengan ID: {merchant_id}")
    except Exception as e:
        await update.message.reply_text(f"❌ Gagal menambahkan merchant: {str(e)}")
    
    return ConversationHandler.END

async def list_merchants(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List semua merchant"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_USER_ID and not is_admin(user_id):
        await update.message.reply_text("❌ Akses ditolak.")
        return
    
    merchants = get_merchants()
    
    if not merchants:
        await update.message.reply_text("📭 Belum ada merchant yang terdaftar.")
        return
    
    merchants_text = "*🏪 DAFTAR MERCHANT*\n\n"
    
    for merchant in merchants:
        merchants_text += f"""
🆔 ID: {merchant[0]}
🏪 Nama: {merchant[1]}
🧾 QRIS Statis: {merchant[2][:50]}...
🕐 Tanggal: {merchant[3]}

{'-' * 30}
"""
    
    await update.message.reply_text(merchants_text, parse_mode='Markdown')

async def add_admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tambah admin baru"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("❌ Hanya super admin yang bisa menambah admin.")
        return
    
    await update.message.reply_text("Masukkan User ID Telegram admin baru:")
    return 1  # State untuk input user ID

async def admin_user_id_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Input User ID admin baru"""
    try:
        new_admin_id = int(update.message.text.strip())
        username = update.message.from_user.username
        
        if add_admin(new_admin_id, username):
            await update.message.reply_text(f"✅ User ID {new_admin_id} berhasil ditambahkan sebagai admin.")
        else:
            await update.message.reply_text("❌ User ID tersebut sudah menjadi admin.")
    except ValueError:
        await update.message.reply_text("❌ User ID tidak valid.")
    except Exception as e:
        await update.message.reply_text(f"❌ Gagal menambahkan admin: {str(e)}")
    
    return ConversationHandler.END

async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast pesan ke semua user"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_USER_ID and not is_admin(user_id):
        await update.message.reply_text("❌ Akses ditolak.")
        return
    
    await update.message.reply_text("Masukkan pesan yang akan di-broadcast:")
    return 1  # State untuk input pesan

async def broadcast_message_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Input pesan broadcast"""
    message = update.message.text
    
    # Di sini kamu bisa mengimplementasikan broadcast ke semua user
    # Untuk sementara, kita hanya menampilkan pesan
    
    await update.message.reply_text(f"📢 Pesan broadcast:\n\n{message}\n\n(Fitur broadcast akan diimplementasikan)")
    
    return ConversationHandler.END