# qris_generator.py
import qrcode
import io
from utils.crc16 import convert_crc16
from database import add_transaction

def generate_dynamic_qris(qris_static: str, amount: str, service_fee: str = "0", merchant_id: int = None):
    """Generate QRIS dinamis dari QRIS statis"""
    
    # Hapus CRC lama (4 digit terakhir)
    qris = qris_static[:-4]
    
    # Ubah dari statis ke dinamis
    step1 = qris.replace("010211", "010212")
    step2 = step1.split("5802ID")
    
    if len(step2) < 2:
        raise ValueError("Data QRIS tidak valid")
    
    # Format amount
    uang = "54" + f"{len(amount):02d}" + amount
    
    # Tambahkan biaya layanan jika ada
    if service_fee and service_fee != "0":
        tax = "55020256" + f"{len(service_fee):02d}" + service_fee
        uang += tax + "5802ID"
    else:
        uang += "5802ID"
    
    # Gabungkan kembali
    fix = step2[0] + uang + step2[1]
    fix += convert_crc16(fix)
    
    return fix

def create_qr_code(data: str) -> bytes:
    """Buat QR Code dari data"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return img_byte_arr.getvalue()