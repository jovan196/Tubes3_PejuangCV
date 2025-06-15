import flet as ft
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from src.frontend.app import main_app

if __name__ == "__main__":
    # Ekstrak CV dari PDF ke CSV sebelum run aplikasi
    try:
        import cv2csv
        cv2csv.main()
        print("✅ Ekstraksi CV ke CSV berhasil.")
    except Exception as e:
        print(f"❌ Error ketika ekstraksi CV ke CSV: {e}")
    # Jalankan aplikasi Flet
    ft.app(target=main_app)