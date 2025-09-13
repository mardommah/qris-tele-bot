# handlers/admin.py
"""Admin handlers for the QRIS Telegram bot."""

import os
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from services.database_service import db_service
from config import ADMIN_USER_ID
from utils.qris_reader import read_qris_from_bytes
from services.telegram_service import telegram_service
from services.logging_service import get_logger

logger = get_logger(__name__)

# State definitions
MERCHANT_USERNAME_INPUT, MERCHANT_NAME_INPUT, MERCHANT_IMAGE_INPUT, MERCHANT_CONFIRMATION = range(4)

async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin menu"""
    user_id = update.effective_user.id
    logger.info(f"User {user_id} accessed admin menu")
    
    # Cek apakah user adalah admin
    if user_id != ADMIN_USER_ID and not db_service.is_admin(user_id):
        merchants = db_service.get_user_merchants(user_id)
        if merchants:
            merchant_list = "\n".join([f"🏪 {m[1]} (ID: {m[0]})" for m in merchants])
            await update.message.reply_text(f"👋 Halo! Berikut adalah merchant Anda:\n\n{merchant_list}\n\nGunakan command /start untuk kembali ke menu utama.")
            logger.info(f"User {user_id} is not admin but has merchant")
            return
        else:
            await update.message.reply_text("📭 Anda belum memiliki merchant. Hubungi admin untuk setup")
            logger.info(f"User {user_id} is not admin and has no merchant")
            return
    
    admin_text = """
👑 *ADMIN MENU*

🔧 *Fitur Admin:*
• /add_merchant - Tambah merchant QRIS
- /add_merchant_for_user - Tambah merchant untuk user lain
• /list_merchants - Lihat semua merchant
• /add_admin - Tambah admin baru
• /broadcast - Kirim pesan ke semua user

Gunakan command di atas untuk mengakses fitur admin.
"""
    
    await update.message.reply_text(admin_text, parse_mode='Markdown')

async def add_merchant_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start adding merchant"""
    user_id = update.effective_user.id
    logger.info(f"User {user_id} started adding merchant")
    
    if user_id != ADMIN_USER_ID and not db_service.is_admin(user_id):
        await update.message.reply_text("❌ Akses ditolak.")
        logger.warning(f"User {user_id} denied access to add merchant")
        return ConversationHandler.END
    
    existing_merchant = db_service.get_user_merchants(user_id)
    if existing_merchant and user_id != ADMIN_USER_ID and not db_service.is_admin(user_id):
        await update.message.reply_text("❌ Anda sudah memiliki merchant. Hubungi admin jika ingin menambahkan merchant baru.")
        logger.info(f"User {user_id} already has a merchant")
        return ConversationHandler.END
        
    await update.message.reply_text("Masukkan nama merchant:")
    return MERCHANT_NAME_INPUT

async def add_merchant_for_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start adding merchant for another user"""
    user_id = update.effective_user.id
    logger.info(f"User {user_id} started adding merchant for another user")
    
    if user_id != ADMIN_USER_ID and not db_service.is_admin(user_id):
        await update.message.reply_text("❌ Akses ditolak.")
        logger.warning(f"User {user_id} denied access to add merchant for user")
        return ConversationHandler.END
    
    await update.message.reply_text("Masukkan User ID Telegram user yang akan didaftarkan:")
    return MERCHANT_USERNAME_INPUT


async def merchant_user_id_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user ID input for merchant"""
    try:
        target_user_id = int(update.message.text.strip())
        context.user_data['target_user_id'] = target_user_id
        logger.info(f"User {update.effective_user.id} entered target user ID: {target_user_id}")
        
        # Cek apakah user sudah punya merchant
        existing_merchant = db_service.get_user_merchants(target_user_id)
        if existing_merchant:
            await update.message.reply_text(f"❌ User ID {target_user_id} sudah memiliki merchant.")
            logger.info(f"Target user {target_user_id} already has a merchant")
            return ConversationHandler.END
        
        await update.message.reply_text("Masukkan nama merchant untuk user tersebut:")
        return MERCHANT_NAME_INPUT
        
    except ValueError:
        logger.warning(f"User {update.effective_user.id} entered invalid target user ID: {update.message.text.strip()}")
        await update.message.reply_text("❌ User ID tidak valid. Masukkan angka User ID Telegram:")
        return MERCHANT_USERNAME_INPUT


async def merchant_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle merchant name input"""
    name = update.message.text.strip()
    logger.info(f"User {update.effective_user.id} entered merchant name: {name}")
    
    if not name:
        logger.warning(f"User {update.effective_user.id} entered empty merchant name")
        await update.message.reply_text("❌ Nama merchant tidak boleh kosong. Silakan masukkan nama merchant:")
        return MERCHANT_NAME_INPUT
    
    context.user_data['merchant_name'] = name
    
    await update.message.reply_text("Silakan upload gambar QRIS merchant:")
    return MERCHANT_IMAGE_INPUT


async def merchant_image_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle merchant QRIS image input"""
    try:
         # Cek apakah pesan mengandung photo
        if not update.message.photo:
            logger.warning(f"User {update.effective_user.id} did not send a photo")
            await update.message.reply_text("❌ Silakan upload gambar QRIS merchant:")
            return MERCHANT_IMAGE_INPUT
        # Dapatkan file photo
        photo = update.message.photo[-1]  # Ambil kualitas tertinggi
        file = await photo.get_file()
        
        # Buat folder jika belum ada
        os.makedirs('static/qris_images', exist_ok=True)
        
        # Simpan file
        file_path = f"static/qris_images/merchant_{update.effective_user.id}_{photo.file_id}.jpg"
        await file.download_to_drive(file_path)
        logger.info(f"User {update.effective_user.id} uploaded QRIS image to: {file_path}")
        
        # Baca QRIS dari gambar
        with open(file_path, 'rb') as f:
            image_bytes = f.read()
        
        qris_data = read_qris_from_bytes(image_bytes)
         # Validasi QRIS data
        if not qris_data or len(qris_data) < 10:
            await update.message.reply_text("❌ QRIS tidak valid. Silakan upload gambar QRIS yang jelas dan benar:")
            # Hapus file yang tidak valid
            if os.path.exists(file_path):
                os.remove(file_path)
            logger.warning(f"User {update.effective_user.id} uploaded invalid QRIS image")
            return MERCHANT_IMAGE_INPUT
        
        # Simpan ke context
        context.user_data['merchant_qris'] = qris_data
        context.user_data['merchant_image_path'] = file_path
        
        # Konfirmasi data
        confirmation_text = f"""
✅ QRIS berhasil dibaca!

🏪 Nama Merchant: {context.user_data['merchant_name']}
🧾 QRIS Data: {qris_data[:100]}...

Apakah data ini sudah benar? (Ya/Tidak)
"""
        
        await update.message.reply_text(confirmation_text)
        return MERCHANT_CONFIRMATION
        
    except Exception as e:
        logger.error(f"Error reading QRIS for user {update.effective_user.id}: {e}")
        await update.message.reply_text(f"❌ Gagal membaca QRIS: {str(e)}\n\nSilakan upload gambar QRIS yang jelas.")
        return MERCHANT_IMAGE_INPUT


async def merchant_confirmation_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle merchant confirmation"""
    user_response = update.message.text.strip().lower()
    logger.info(f"User {update.effective_user.id} confirmed merchant data: {user_response}")
    
    if user_response == 'ya' or user_response == 'y':
        try:
            # Tentukan owner Telegram ID
            target_user_id = context.user_data.get('target_user_id', update.effective_user.id)

            # Simpan merchant ke database
            merchant_id = db_service.add_merchant(
                name=context.user_data['merchant_name'],
                qris_static=context.user_data['merchant_qris'],
                owner_telegram_id=target_user_id,
                qris_image_path=context.user_data['merchant_image_path']
            )
            
            success_text = f"""
✅ Merchant berhasil ditambahkan!

🆔 ID Merchant: {merchant_id}
🏪 Nama: {context.user_data['merchant_name']}
🧾 QRIS: {context.user_data['merchant_qris'][:50]}...

Merchant siap digunakan untuk generate QRIS dinamis.
"""
            
            await update.message.reply_text(success_text, reply_markup=telegram_service.remove_reply_keyboard())
            
            # Bersihkan context
            context.user_data.clear()
            
            logger.info(f"Merchant added successfully with ID: {merchant_id} for user {target_user_id}")
            return ConversationHandler.END
            
        except Exception as e:
            logger.error(f"Error saving merchant for user {update.effective_user.id}: {e}")
            await update.message.reply_text(f"❌ Gagal menyimpan merchant: {str(e)}")
            return ConversationHandler.END
            
    elif user_response == 'tidak' or user_response == 't':
        logger.info(f"User {update.effective_user.id} rejected merchant data")
        await update.message.reply_text("❌ Silakan upload ulang gambar QRIS yang benar.")
        return MERCHANT_IMAGE_INPUT
    else:
        logger.warning(f"User {update.effective_user.id} entered invalid confirmation: {user_response}")
        await update.message.reply_text("❌ Pilihan tidak valid. Jawab 'Ya' atau 'Tidak'.")
        return MERCHANT_CONFIRMATION


async def list_merchants(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all merchants"""
    user_id = update.effective_user.id
    logger.info(f"User {user_id} requested merchant list")
    
    if user_id != ADMIN_USER_ID and not db_service.is_admin(user_id):
        await update.message.reply_text("❌ Akses ditolak.")
        logger.warning(f"User {user_id} denied access to merchant list")
        return
    
    merchants = db_service.get_merchants()
    
    if not merchants:
        await update.message.reply_text("📭 Belum ada merchant yang terdaftar.")
        logger.info(f"No merchants found for user {user_id}")
        return
    
    merchants_text = "*🏪 DAFTAR MERCHANT*\n\n"
    
    for merchant in merchants:
        merchants_text += f"""
🆔 ID: {merchant[0]}
🏪 Nama: {merchant[1]}
🧾 QRIS Statis: {merchant[2][:50]}...
📸 Gambar: {'✅ Ada' if merchant[3] else '❌ Tidak Ada'}
👤 Owner: {merchant[4]}
🕐 Tanggal: {merchant[5]}

{'-' * 30}
"""
    
    await update.message.reply_text(merchants_text, parse_mode='Markdown')

async def add_admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add new admin"""
    user_id = update.effective_user.id
    logger.info(f"User {user_id} started adding admin")
    
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("❌ Hanya super admin yang bisa menambah admin.")
        logger.warning(f"User {user_id} denied access to add admin")
        return
    
    await update.message.reply_text("Masukkan User ID Telegram admin baru:")
    return 1  # State untuk input user ID

async def admin_user_id_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin user ID input"""
    try:
        new_admin_id = int(update.message.text.strip())
        username = update.message.from_user.username
        logger.info(f"User {update.effective_user.id} entered new admin ID: {new_admin_id}")
        
        if db_service.add_admin(new_admin_id, username):
            await update.message.reply_text(f"✅ User ID {new_admin_id} berhasil ditambahkan sebagai admin.")
            logger.info(f"Admin {new_admin_id} added successfully")
        else:
            await update.message.reply_text("❌ User ID tersebut sudah menjadi admin.")
            logger.info(f"User {new_admin_id} is already an admin")
    except ValueError:
        logger.warning(f"User {update.effective_user.id} entered invalid admin ID: {update.message.text.strip()}")
        await update.message.reply_text("❌ User ID tidak valid.")
    except Exception as e:
        logger.error(f"Error adding admin {new_admin_id} by user {update.effective_user.id}: {e}")
        await update.message.reply_text(f"❌ Gagal menambahkan admin: {str(e)}")
    
    return ConversationHandler.END

async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast message to all users"""
    user_id = update.effective_user.id
    logger.info(f"User {user_id} started broadcast")
    
    if user_id != ADMIN_USER_ID and not db_service.is_admin(user_id):
        await update.message.reply_text("❌ Akses ditolak.")
        logger.warning(f"User {user_id} denied access to broadcast")
        return
    
    await update.message.reply_text("Masukkan pesan yang akan di-broadcast:")
    return 1  # State untuk input pesan

async def broadcast_message_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle broadcast message input"""
    message = update.message.text
    logger.info(f"User {update.effective_user.id} entered broadcast message: {message}")
    
    # Di sini kamu bisa mengimplementasikan broadcast ke semua user
    # Untuk sementara, kita hanya menampilkan pesan
    
    await update.message.reply_text(f"📢 Pesan broadcast:\n\n{message}\n\n(Fitur broadcast akan diimplementasikan)")
    
    return ConversationHandler.END