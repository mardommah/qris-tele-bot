# utils/qris_reader.py
import cv2
from pyzbar import pyzbar
from PIL import Image
import numpy as np

def read_qris_from_image(image_path: str) -> str:
    """
    Baca QRIS dari gambar menggunakan pyzbar
    """
    try:
        # Baca gambar menggunakan OpenCV
        image = cv2.imread(image_path)
        if image is None:
            raise Exception("Gagal membaca gambar")
        
        # Decode QR code
        decoded_objects = pyzbar.decode(image)
        
        if decoded_objects:
            # Ambil data QR code pertama
            qris_data = decoded_objects[0].data.decode('utf-8')
            return qris_data
        else:
            raise Exception("Tidak dapat membaca QR code dari gambar")
            
    except Exception as e:
        raise Exception(f"Gagal membaca QRIS: {str(e)}")

def read_qris_from_bytes(image_bytes: bytes) -> str:
    """
    Baca QRIS dari bytes gambar
    """
    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise Exception("Gagal membaca gambar dari bytes")
        
        # Decode QR code
        decoded_objects = pyzbar.decode(image)
        
        if decoded_objects:
            qris_data = decoded_objects[0].data.decode('utf-8')
            return qris_data
        else:
            raise Exception("Tidak dapat membaca QR code dari gambar")
            
    except Exception as e:
        raise Exception(f"Gagal membaca QRIS: {str(e)}")