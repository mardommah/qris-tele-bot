# handlers/admin.py
import os
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from database import add_merchant, get_merchants, add_admin, is_admin, get_user_merchants, toggle_merchant_status, get_merchant_by_id
from config import ADMIN_USER_ID
from utils.qris_reader import read_qris_from_bytes
from telegram import ReplyKeyboardRemove


# State definitions
MERCHANT_USERNAME_INPUT, MERCHANT_NAME_INPUT, MERCHANT_IMAGE_INPUT, MERCHANT_CONFIRMATION = range(4)

async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menu Admin"""
    user_id = update.effective_user.id
    
    # Cek apakah user adalah admin
    if user_id != ADMIN_USER_ID and not is_admin(user_id):
        merchants = get_user_merchants(user_id)
        if merchants:
            merchant_list = "\n".join([f"🏪 {m[1]} (ID: {m[0]})" for m in merchants])
            await update.message.reply_text(f"👋 Halo! Berikut adalah merchant Anda:\n\n{merchant_list}\n\nGunakan command /start untuk kembali ke menu utama.")
            return
        else:
            await update.message.reply_text("📭 Anda belum memiliki merchant. Hubungi admin untuk setup")
        return
    
    admin_text = """
👑 *ADMIN MENU*

🔧 *Fitur Admin:*
• /add_merchant - Tambah merchant QRIS
- /add_merchant_for_user - Tambah merchant untuk user lain
• /list_merchants - Lihat semua merchant
• /toggle_merchant - Aktifkan/Nonaktifkan merchant
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
    
    existing_merchant = get_user_merchants(user_id)
    if existing_merchant and user_id != ADMIN_USER_ID and not is_admin(user_id):
        await update.message.reply_text("❌ Anda sudah memiliki merchant. Hubungi admin jika ingin menambahkan merchant baru.")
        return ConversationHandler.END
        
    await update.message.reply_text("Masukkan nama merchant:")
    return MERCHANT_NAME_INPUT

async def add_merchant_for_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mulai tambah merchant untuk user lain"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_USER_ID and not is_admin(user_id):
        await update.message.reply_text("❌ Akses ditolak.")
        return ConversationHandler.END
    
    await update.message.reply_text("Masukkan User ID Telegram user yang akan didaftarkan:")
    return MERCHANT_USERNAME_INPUT


async def merchant_user_id_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Input User ID user yang akan didapat merchant"""
    try:
        target_user_id = int(update.message.text.strip())
        context.user_data['target_user_id'] = target_user_id
        
        # Cek apakah user sudah punya merchant
        existing_merchant = get_user_merchants(target_user_id)
        if existing_merchant:
            await update.message.reply_text(f"❌ User ID {target_user_id} sudah memiliki merchant.")
            return ConversationHandler.END
        
        await update.message.reply_text("Masukkan nama merchant untuk user tersebut:")
        return MERCHANT_NAME_INPUT
        
    except ValueError:
        await update.message.reply_text("❌ User ID tidak valid. Masukkan angka User ID Telegram:")
        return MERCHANT_USERNAME_INPUT


async def merchant_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Input nama merchant"""
    name = update.message.text.strip()
    if not name:
        await update.message.reply_text("❌ Nama merchant tidak boleh kosong. Silakan masukkan nama merchant:")
        return MERCHANT_NAME_INPUT
    
    context.user_data['merchant_name'] = name
    
    await update.message.reply_text("Silakan upload gambar QRIS merchant:")
    return MERCHANT_IMAGE_INPUT


async def merchant_image_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Input gambar QRIS merchant"""
    try:
         # Cek apakah pesan mengandung photo
        if not update.message.photo:
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
        await update.message.reply_text(f"❌ Gagal membaca QRIS: {str(e)}\n\nSilakan upload gambar QRIS yang jelas.")
        return MERCHANT_IMAGE_INPUT


async def merchant_confirmation_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Konfirmasi data merchant"""
    user_response = update.message.text.strip().lower()
    
    if user_response == 'ya' or user_response == 'y':
        try:
            # Tentukan owner Telegram ID
            target_user_id = context.user_data.get('target_user_id', update.effective_user.id)

            # Simpan merchant ke database
            merchant_id = add_merchant(
                name=context.user_data['merchant_name'],
                qris_static=context.user_data['merchant_qris'],
                owner_telegram_id=target_user_id,
                qris_image_path=context.user_data['merchant_image_path'],
                is_active=True  # Default subscription status is active
            )
            
            success_text = f"""
✅ Merchant berhasil ditambahkan!

🆔 ID Merchant: {merchant_id}
🏪 Nama: {context.user_data['merchant_name']}
🧾 QRIS: {context.user_data['merchant_qris'][:50]}...

Merchant siap digunakan untuk generate QRIS dinamis.
"""
            
            await update.message.reply_text(success_text, reply_markup=ReplyKeyboardRemove())
            
            # Bersihkan context
            context.user_data.clear()
            
            return ConversationHandler.END
            
        except Exception as e:
            await update.message.reply_text(f"❌ Gagal menyimpan merchant: {str(e)}")
            return ConversationHandler.END
            
    elif user_response == 'tidak' or user_response == 't':
        await update.message.reply_text("❌ Silakan upload ulang gambar QRIS yang benar.")
        return MERCHANT_IMAGE_INPUT
    else:
        await update.message.reply_text("❌ Pilihan tidak valid. Jawab 'Ya' atau 'Tidak'.")
        return MERCHANT_QRIS_INPUT



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
        is_active = "✅ Aktif" if (len(merchant) > 6 and merchant[6]) else "❌ Nonaktif"
        merchants_text += f"""
🆔 ID: {merchant[0]}
🏪 Nama: {merchant[1]}
🧾 QRIS Statis: {merchant[2][:50]}...
📸 Gambar: {'✅ Ada' if merchant[3] else '❌ Tidak Ada'}
👤 Owner: {merchant[4]}
📊 Status: {is_active}
🕐 Tanggal: {merchant[5]}

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

async def toggle_merchant_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle status merchant"""
    user_id = update.effective_user.id
    
    if user_id != ADMIN_USER_ID and not is_admin(user_id):
        await update.message.reply_text("❌ Akses ditolak.")
        return
    
    await update.message.reply_text("Masukkan ID merchant yang akan di-toggle statusnya:")
    return 1  # State untuk input merchant ID

async def toggle_merchant_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Input merchant ID untuk toggle status"""
    try:
        merchant_id = int(update.message.text.strip())
        
        # Dapatkan merchant
        merchant = get_merchant_by_id(merchant_id)
        if not merchant:
            await update.message.reply_text("❌ Merchant dengan ID tersebut tidak ditemukan.")
            return ConversationHandler.END
        
        # Toggle status
        current_status = bool(merchant[6]) if len(merchant) > 6 else True  # Default to True if not found
        new_status = not current_status
        
        toggle_merchant_status(merchant_id, new_status)
        
        status_text = "aktif" if new_status else "nonaktif"
        await update.message.reply_text(f"✅ Status merchant '{merchant[1]}' berhasil diubah menjadi {status_text}.")
        
    except ValueError:
        await update.message.reply_text("❌ ID merchant tidak valid.")
    except Exception as e:
        await update.message.reply_text(f"❌ Gagal toggle status merchant: {str(e)}")
    
    return ConversationHandler.END