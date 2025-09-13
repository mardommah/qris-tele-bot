# qris_generator.py
"""QRIS generator - legacy interface for backward compatibility."""

from services.qris_service import qris_service
from typing import Optional

# Legacy functions for backward compatibility
def generate_dynamic_qris(qris_static: str, amount: str, service_fee: str = "0", merchant_id: Optional[int] = None) -> str:
    """Generate dynamic QRIS from static QRIS"""
    return qris_service.generate_dynamic_qris(qris_static, amount, service_fee, merchant_id)

def create_qr_code(data: str) -> bytes:
    """Create QR Code from data"""
    return qris_service.create_qr_code(data)