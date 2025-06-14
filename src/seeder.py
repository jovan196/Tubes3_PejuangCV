# scripts/seed_sample_data.py
"""
Script untuk mengisi database dengan data sample untuk testing.
Jalankan script ini setelah setup database untuk mendapatkan data testing.
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager

def main():
    """Main function untuk seeding data sample"""
    print("=== ATS Database Seeder ===")
    print("Memulai proses seeding data sample...")
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    if not db_manager.connection:
        print("❌ Gagal koneksi ke database!")
        return False
    
    # Create tables
    print("📋 Membuat tabel database...")
    if not db_manager.create_tables():
        print("❌ Gagal membuat tabel!")
        return False
    
    print("✅ Tabel berhasil dibuat!")
    
    # Seed sample data
    print("🌱 Mengisi data sample...")
    if not db_manager.seed_sample_data():
        print("❌ Gagal mengisi data sample!")
        return False
    
    print("✅ Data sample berhasil diisi!")
    
    # Show statistics
    print("\n📊 Statistik Database:")
    stats = db_manager.get_statistics()
    
    if stats:
        print(f"   - Total Pelamar: {stats.get('total_applicants', 0)}")
        print(f"   - Total Aplikasi Aktif: {stats.get('active_applications', 0)}")
        
        if 'applications_by_role' in stats:
            print("\n   Aplikasi berdasarkan posisi:")
            for role, count in stats['applications_by_role']:
                print(f"     • {role}: {count} aplikasi")
    
    # Close connection
    db_manager.disconnect()
    
    print("\n✅ Seeding selesai! Database siap digunakan.")
    print("\n💡 Tips:")
    print("   1. Pastikan file CV sample ada di directory 'data/'")
    print("   2. Jalankan aplikasi utama dengan: python main.py")
    print("   3. Gunakan keyword seperti: Python, React, JavaScript untuk testing")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)