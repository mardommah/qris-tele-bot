# services/qris_service.py
"""QRIS service for handling QRIS operations."""

import qrcode
import io
from typing import Optional
from utils.crc16 import convert_crc16
from services.logging_service import get_logger

logger = get_logger(__name__)


class QrisService:
    """Service class for QRIS operations."""
    
    def generate_dynamic_qris(self, qris_static: str, amount: str, service_fee: str = "0", 
                             merchant_id: Optional[int] = None) -> str:
        """Generate dynamic QRIS from static QRIS."""
        try:
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
            
            logger.info(f"Dynamic QRIS generated for merchant ID: {merchant_id}")
            return fix
        except Exception as e:
            logger.error(f"Error generating dynamic QRIS: {e}")
            raise

    def create_qr_code(self, data: str) -> bytes:
        """Create QR Code from data."""
        try:
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
            
            logger.info("QR Code created successfully")
            return img_byte_arr.getvalue()
        except Exception as e:
            logger.error(f"Error creating QR Code: {e}")
            raise


# Create a global instance
qris_service = QrisService()