# utils/crc16.py
def convert_crc16(data: str) -> str:
    """Generate CRC16 untuk QRIS"""
    crc = 0xFFFF
    for ch in data:
        crc ^= (ord(ch) << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF  # jaga agar tetap 16-bit
    return format(crc, '04X')