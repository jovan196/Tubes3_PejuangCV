# run_ats.py
"""
Startup script untuk ATS System.
Script ini memastikan semua dependencies terinstall dan database ter-setup
sebelum menjalankan aplikasi utama.
"""

import sys
import os
import subprocess
import importlib

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 atau lebih tinggi diperlukan!")
        print(f"   Versi saat ini: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} - OK")
    return True

def check_and_install_dependencies():
    """Check and install required dependencies"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'flet',
        'mysql-connector-python',
        'PyPDF2',
        'PyMuPDF',
        'python-dateutil'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PyMuPDF':
                import fitz
            elif package == 'mysql-connector-python':
                import mysql.connector
            elif package == 'python-dateutil':
                import dateutil
            else:
                importlib.import_module(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install'
            ] + missing_packages)
            print("✅ Dependencies installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies!")
            print("💡 Try running: pip install -r requirements.txt")
            return False
    
    return True

def check_database_connection():
    """Check MySQL database connection"""
    print("🗄️  Checking database connection...")
    
    try:
        sys.path.append('src')
        from database.db_manager import DatabaseManager
        
        db = DatabaseManager()
        if db.connection and db.connection.is_connected():
            print("   ✅ Database connection - OK")
            
            # Check if tables exist
            cursor = db.connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            required_tables = ['ApplicantProfile', 'ApplicationDetail']
            existing_tables = [table[0] for table in tables]
            
            missing_tables = [t for t in required_tables if t not in existing_tables]
            
            if missing_tables:
                print(f"   ⚠️  Missing tables: {missing_tables}")
                print("   🔧 Creating tables...")
                if db.create_tables():
                    print("   ✅ Tables created successfully")
                else:
                    print("   ❌ Failed to create tables")
                    return False
            else:
                print("   ✅ Database tables - OK")
            
            # Check if database has data
            cursor.execute("SELECT COUNT(*) FROM ApplicantProfile")
            applicant_count = cursor.fetchone()[0]
            
            if applicant_count == 0:
                print("   📝 Database is empty, seeding sample data...")
                if db.seed_sample_data():
                    print("   ✅ Sample data created")
                else:
                    print("   ⚠️  Failed to create sample data")
            else:
                print(f"   ✅ Database has {applicant_count} applicants")
            
            cursor.close()
            db.disconnect()
            return True
        else:
            print("   ❌ Cannot connect to database")
            print("   💡 Check MySQL server and credentials in src/database/db_manager.py")
            return False
            
    except Exception as e:
        print(f"   ❌ Database check failed: {e}")
        print("   💡 Ensure MySQL is installed and running")
        return False

def check_data_directory():
    """Check and create data directory for CV files"""
    print("📁 Checking data directory...")
    
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"   ✅ Created {data_dir}/ directory")
    else:
        print(f"   ✅ {data_dir}/ directory exists")
    
    # Check for PDF files
    pdf_files = [f for f in os.listdir(data_dir) if f.lower().endswith('.pdf')]
    
    if pdf_files:
        print(f"   ✅ Found {len(pdf_files)} PDF files")
    else:
        print("   ⚠️  No PDF files found in data/ directory")
        print("   💡 Add PDF CV files to data/ directory for testing")
    
    return True

def run_system_tests():
    """Run basic system tests"""
    print("🧪 Running system tests...")
    
    try:
        sys.path.append('src')
        
        # Test algorithms
        from algorithms.kmp import KMPSearch
        from algorithms.boyer_moore import BoyerMooreSearch
        from algorithms.levenshtein import LevenshteinDistance
        from algorithms.encryption import DataEncryption
        
        # Quick algorithm tests
        kmp = KMPSearch()
        assert kmp.search("hello world", "world") == 6
        
        bm = BoyerMooreSearch()
        assert bm.search("hello world", "world") == 6
        
        lev = LevenshteinDistance()
        assert lev.distance("hello", "hello") == 0
        
        enc = DataEncryption()
        test_text = "test"
        encrypted = enc.encrypt(test_text)
        assert enc.decrypt(encrypted) == test_text
        
        print("   ✅ Algorithm tests passed")
        
        # Test utilities
        from utils.pdf_extractor import PDFExtractor
        from utils.regex_extractor import RegexExtractor
        
        pdf_ext = PDFExtractor()
        regex_ext = RegexExtractor()
        
        # Test regex extraction
        test_cv = "Python Java JavaScript React Email: test@example.com Phone: +6281234567890"
        extracted = regex_ext.extract_cv_info(test_cv)
        
        assert len(extracted['skills']) > 0
        assert len(extracted['emails']) > 0
        assert len(extracted['phones']) > 0
        
        print("   ✅ Utility tests passed")
        
        return True
        
    except Exception as e:
        print(f"   ❌ System tests failed: {e}")
        return False

def display_startup_info():
    """Display startup information"""
    print("=" * 60)
    print("🚀 ATS SYSTEM - APPLICANT TRACKING SYSTEM")
    print("=" * 60)
    print("📋 Tugas Besar 3 IF2211 Strategi Algoritma")
    print("🏫 Institut Teknologi Bandung")
    print("📅 Semester II 2024/2025")
    print("=" * 60)

def display_ready_message():
    """Display ready message with instructions"""
    print("\n" + "=" * 60)
    print("🎉 ATS SYSTEM READY!")
    print("=" * 60)
    print("💡 Petunjuk Penggunaan:")
    print("   1. Masukkan kata kunci (pisahkan dengan koma)")
    print("   2. Pilih algoritma: KMP, Boyer-Moore, atau Aho-Corasick")
    print("   3. Tentukan jumlah CV yang ditampilkan")
    print("   4. Klik 'Mulai Pencarian CV'")
    print("\n🔍 Contoh kata kunci: Python, React, JavaScript, SQL")
    print("📄 File CV harus dalam format PDF di folder data/")
    print("=" * 60)

def main():
    """Main startup function"""
    display_startup_info()
    
    # System checks
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_and_install_dependencies),
        ("Database", check_database_connection),
        ("Data Directory", check_data_directory),
        ("System Tests", run_system_tests)
    ]
    
    failed_checks = []
    
    for check_name, check_function in checks:
        print(f"\n{check_name}...")
        try:
            if not check_function():
                failed_checks.append(check_name)
        except Exception as e:
            print(f"   ❌ {check_name} failed: {e}")
            failed_checks.append(check_name)
    
    if failed_checks:
        print(f"\n⚠️  System checks completed with issues:")
        for check in failed_checks:
            print(f"   • {check}")
        
        print(f"\n❓ Continue anyway? (y/n): ", end="")
        response = input().lower().strip()
        
        if response != 'y' and response != 'yes':
            print("🛑 Startup cancelled")
            sys.exit(1)
        
        print("⚠️  Starting with warnings...")
    else:
        print("\n✅ All system checks passed!")
    
    display_ready_message()
    
    # Start the main application
    print("\n🚀 Starting ATS System...")
    
    try:
        sys.path.append('src')
        from main import main as app_main
        import flet as ft
        
        ft.app(target=app_main)
        
    except KeyboardInterrupt:
        print("\n👋 ATS System stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        print("💡 Check error details above and try again")
        sys.exit(1)

if __name__ == "__main__":
    main()