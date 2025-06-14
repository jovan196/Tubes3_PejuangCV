# database/db_manager.py
import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Optional, Tuple
import os
from algorithms.encryption import DataEncryption

class DatabaseManager:
    """
    Manager untuk operasi database MySQL.
    Mengelola koneksi, operasi CRUD, dan integrasi dengan sistem enkripsi.
    """
    
    def __init__(self, 
                 host: str = "localhost", 
                 port: int = 3306,
                 user: str = "root", 
                 password: str = "", 
                 database: str = "ats_database"):
        """
        Inisialisasi Database Manager.
        
        Args:
            host (str): Database host
            port (int): Database port
            user (str): Database username
            password (str): Database password
            database (str): Database name
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.encryption = DataEncryption()
        
        # Fields yang akan dienkripsi
        self.encrypted_fields = ['first_name', 'last_name', 'address', 'phone_number']
        
        self.connect()
    
    def connect(self) -> bool:
        """
        Membuat koneksi ke database MySQL.
        
        Returns:
            bool: True jika koneksi berhasil
        """
        try:
            # Create database if not exists
            temp_connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password
            )
            cursor = temp_connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            cursor.close()
            temp_connection.close()
            
            # Connect to the database
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=True
            )
            
            print(f"Successfully connected to MySQL database: {self.database}")
            return True
            
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return False
    
    def disconnect(self) -> None:
        """Menutup koneksi database."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")
    
    def create_tables(self) -> bool:
        """
        Membuat tabel-tabel yang diperlukan untuk sistem ATS.
        
        Returns:
            bool: True jika berhasil membuat tabel
        """
        try:
            cursor = self.connection.cursor()
            
            # Tabel ApplicantProfile
            create_applicant_table = """
            CREATE TABLE IF NOT EXISTS ApplicantProfile (
                applicant_id INT NOT NULL AUTO_INCREMENT,
                first_name VARCHAR(255) NOT NULL,
                last_name VARCHAR(255) NOT NULL,
                date_of_birth DATE DEFAULT NULL,
                address TEXT DEFAULT NULL,
                phone_number VARCHAR(50) DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                PRIMARY KEY (applicant_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # Tabel ApplicationDetail
            create_application_table = """
            CREATE TABLE IF NOT EXISTS ApplicationDetail (
                detail_id INT NOT NULL AUTO_INCREMENT,
                applicant_id INT NOT NULL,
                application_role VARCHAR(255) NOT NULL,
                cv_path TEXT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(50) DEFAULT 'active',
                PRIMARY KEY (detail_id),
                FOREIGN KEY (applicant_id) REFERENCES ApplicantProfile(applicant_id) 
                    ON DELETE CASCADE ON UPDATE CASCADE,
                INDEX idx_applicant_id (applicant_id),
                INDEX idx_application_role (application_role),
                INDEX idx_status (status)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            cursor.execute(create_applicant_table)
            cursor.execute(create_application_table)
            
            print("Database tables created successfully")
            cursor.close()
            return True
            
        except Error as e:
            print(f"Error creating tables: {e}")
            return False
    
    def insert_applicant(self, first_name: str, last_name: str, 
                        date_of_birth: str = None, address: str = None, 
                        phone_number: str = None) -> Optional[int]:
        """
        Menambahkan data pelamar baru dengan enkripsi.
        
        Args:
            first_name (str): Nama depan
            last_name (str): Nama belakang
            date_of_birth (str): Tanggal lahir (YYYY-MM-DD)
            address (str): Alamat
            phone_number (str): Nomor telepon
            
        Returns:
            Optional[int]: ID pelamar yang baru dibuat, None jika gagal
        """
        try:
            cursor = self.connection.cursor()
            
            # Enkripsi data sensitif
            encrypted_first_name = self.encryption.encrypt(first_name)
            encrypted_last_name = self.encryption.encrypt(last_name)
            encrypted_address = self.encryption.encrypt(address) if address else None
            encrypted_phone = self.encryption.encrypt(phone_number) if phone_number else None
            
            query = """
            INSERT INTO ApplicantProfile 
            (first_name, last_name, date_of_birth, address, phone_number)
            VALUES (%s, %s, %s, %s, %s)
            """
            
            values = (encrypted_first_name, encrypted_last_name, date_of_birth, 
                     encrypted_address, encrypted_phone)
            
            cursor.execute(query, values)
            applicant_id = cursor.lastrowid
            
            cursor.close()
            print(f"Applicant inserted with ID: {applicant_id}")
            return applicant_id
            
        except Error as e:
            print(f"Error inserting applicant: {e}")
            return None
    
    def insert_application(self, applicant_id: int, application_role: str, cv_path: str) -> Optional[int]:
        """
        Menambahkan detail aplikasi lamaran.
        
        Args:
            applicant_id (int): ID pelamar
            application_role (str): Posisi yang dilamar
            cv_path (str): Path file CV
            
        Returns:
            Optional[int]: ID detail aplikasi, None jika gagal
        """
        try:
            cursor = self.connection.cursor()
            
            query = """
            INSERT INTO ApplicationDetail (applicant_id, application_role, cv_path)
            VALUES (%s, %s, %s)
            """
            
            values = (applicant_id, application_role, cv_path)
            cursor.execute(query, values)
            detail_id = cursor.lastrowid
            
            cursor.close()
            print(f"Application inserted with ID: {detail_id}")
            return detail_id
            
        except Error as e:
            print(f"Error inserting application: {e}")
            return None
    
    def get_applicant_by_id(self, applicant_id: int) -> Optional[Dict]:
        """
        Mengambil data pelamar berdasarkan ID dengan dekripsi.
        
        Args:
            applicant_id (int): ID pelamar
            
        Returns:
            Optional[Dict]: Data pelamar atau None jika tidak ditemukan
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            query = "SELECT * FROM ApplicantProfile WHERE applicant_id = %s"
            cursor.execute(query, (applicant_id,))
            result = cursor.fetchone()
            
            if result:
                # Dekripsi data sensitif
                result['first_name'] = self.encryption.decrypt(result['first_name'])
                result['last_name'] = self.encryption.decrypt(result['last_name'])
                if result['address']:
                    result['address'] = self.encryption.decrypt(result['address'])
                if result['phone_number']:
                    result['phone_number'] = self.encryption.decrypt(result['phone_number'])
            
            cursor.close()
            return result
            
        except Error as e:
            print(f"Error getting applicant: {e}")
            return None
    
    def get_cv_details(self, detail_id: int) -> Optional[Dict]:
        """
        Mengambil detail CV berdasarkan detail ID.
        
        Args:
            detail_id (int): ID detail aplikasi
            
        Returns:
            Optional[Dict]: Detail CV atau None jika tidak ditemukan
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            query = "SELECT * FROM ApplicationDetail WHERE detail_id = %s"
            cursor.execute(query, (detail_id,))
            result = cursor.fetchone()
            
            cursor.close()
            return result
            
        except Error as e:
            print(f"Error getting CV details: {e}")
            return None
    
    def get_all_cvs(self) -> List[Dict]:
        """
        Mengambil semua data CV dari database.
        
        Returns:
            List[Dict]: List berisi semua data CV
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
            SELECT ad.*, ap.first_name, ap.last_name, ap.date_of_birth, 
                   ap.address, ap.phone_number
            FROM ApplicationDetail ad
            JOIN ApplicantProfile ap ON ad.applicant_id = ap.applicant_id
            WHERE ad.status = 'active'
            ORDER BY ad.applied_at DESC
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            cursor.close()
            return results
            
        except Error as e:
            print(f"Error getting all CVs: {e}")
            return []
    
    def search_cvs_by_role(self, role: str) -> List[Dict]:
        """
        Mencari CV berdasarkan posisi yang dilamar.
        
        Args:
            role (str): Posisi yang dicari
            
        Returns:
            List[Dict]: List CV yang sesuai
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
            SELECT ad.*, ap.first_name, ap.last_name, ap.date_of_birth,
                   ap.address, ap.phone_number
            FROM ApplicationDetail ad
            JOIN ApplicantProfile ap ON ad.applicant_id = ap.applicant_id
            WHERE ad.application_role LIKE %s AND ad.status = 'active'
            ORDER BY ad.applied_at DESC
            """
            
            cursor.execute(query, (f"%{role}%",))
            results = cursor.fetchall()
            
            cursor.close()
            return results
            
        except Error as e:
            print(f"Error searching CVs by role: {e}")
            return []
    
    def update_applicant(self, applicant_id: int, **kwargs) -> bool:
        """
        Update data pelamar.
        
        Args:
            applicant_id (int): ID pelamar
            **kwargs: Field yang akan diupdate
            
        Returns:
            bool: True jika berhasil update
        """
        try:
            cursor = self.connection.cursor()
            
            # Enkripsi field sensitif jika ada
            for field in self.encrypted_fields:
                if field in kwargs and kwargs[field] is not None:
                    kwargs[field] = self.encryption.encrypt(str(kwargs[field]))
            
            # Build query dinamis
            set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
            query = f"UPDATE ApplicantProfile SET {set_clause} WHERE applicant_id = %s"
            
            values = list(kwargs.values()) + [applicant_id]
            cursor.execute(query, values)
            
            cursor.close()
            print(f"Applicant {applicant_id} updated successfully")
            return True
            
        except Error as e:
            print(f"Error updating applicant: {e}")
            return False
    
    def delete_applicant(self, applicant_id: int) -> bool:
        """
        Menghapus data pelamar (soft delete).
        
        Args:
            applicant_id (int): ID pelamar
            
        Returns:
            bool: True jika berhasil delete
        """
        try:
            cursor = self.connection.cursor()
            
            # Soft delete - update status aplikasi menjadi inactive
            query = "UPDATE ApplicationDetail SET status = 'inactive' WHERE applicant_id = %s"
            cursor.execute(query, (applicant_id,))
            
            cursor.close()
            print(f"Applicant {applicant_id} deleted (soft delete)")
            return True
            
        except Error as e:
            print(f"Error deleting applicant: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """
        Mengambil statistik database.
        
        Returns:
            Dict: Statistik database
        """
        try:
            cursor = self.connection.cursor()
            
            stats = {}
            
            # Total applicants
            cursor.execute("SELECT COUNT(*) FROM ApplicantProfile")
            stats['total_applicants'] = cursor.fetchone()[0]
            
            # Total active applications
            cursor.execute("SELECT COUNT(*) FROM ApplicationDetail WHERE status = 'active'")
            stats['active_applications'] = cursor.fetchone()[0]
            
            # Applications by role
            cursor.execute("""
                SELECT application_role, COUNT(*) as count 
                FROM ApplicationDetail 
                WHERE status = 'active' 
                GROUP BY application_role 
                ORDER BY count DESC
            """)
            stats['applications_by_role'] = cursor.fetchall()
            
            cursor.close()
            return stats
            
        except Error as e:
            print(f"Error getting statistics: {e}")
            return {}
    
    def seed_sample_data(self) -> bool:
        """
        Mengisi database dengan data sample untuk testing.
        
        Returns:
            bool: True jika berhasil seed data
        """
        try:
            # Sample applicants data
            sample_applicants = [
                ("Ahmad", "Rizki", "1995-05-15", "Jl. Sudirman No. 123, Jakarta", "081234567890"),
                ("Sari", "Dewi", "1992-08-20", "Jl. Thamrin No. 456, Jakarta", "081234567891"),
                ("Budi", "Santoso", "1990-12-10", "Jl. Gatot Subroto No. 789, Jakarta", "081234567892"),
                ("Maya", "Putri", "1994-03-25", "Jl. Kuningan No. 101, Jakarta", "081234567893"),
                ("Andi", "Pratama", "1991-07-30", "Jl. Senayan No. 202, Jakarta", "081234567894"),
                ("Lisa", "Chen", "1993-11-12", "Jl. Kemang No. 303, Jakarta", "081234567895"),
                ("Rudi", "Hermawan", "1989-09-18", "Jl. Menteng No. 404, Jakarta", "081234567896"),
                ("Nina", "Sari", "1996-01-08", "Jl. Cikini No. 505, Jakarta", "081234567897"),
                ("Doni", "Wijaya", "1988-04-22", "Jl. Tanah Abang No. 606, Jakarta", "081234567898"),
                ("Eka", "Putri", "1997-06-14", "Jl. Salemba No. 707, Jakarta", "081234567899")
            ]
            
            # Sample applications data (role, cv_path)
            sample_applications = [
                ("Software Engineer", "cv_001_ahmad_rizki.pdf"),
                ("Data Scientist", "cv_002_sari_dewi.pdf"),
                ("Frontend Developer", "cv_003_budi_santoso.pdf"),
                ("UI/UX Designer", "cv_004_maya_putri.pdf"),
                ("Backend Developer", "cv_005_andi_pratama.pdf"),
                ("Product Manager", "cv_006_lisa_chen.pdf"),
                ("DevOps Engineer", "cv_007_rudi_hermawan.pdf"),
                ("Mobile Developer", "cv_008_nina_sari.pdf"),
                ("Machine Learning Engineer", "cv_009_doni_wijaya.pdf"),
                ("Quality Assurance", "cv_010_eka_putri.pdf")
            ]
            
            # Insert applicants and applications
            for i, (first_name, last_name, dob, address, phone) in enumerate(sample_applicants):
                applicant_id = self.insert_applicant(first_name, last_name, dob, address, phone)
                if applicant_id:
                    role, cv_path = sample_applications[i]
                    self.insert_application(applicant_id, role, cv_path)
            
            print("Sample data seeded successfully")
            return True
            
        except Exception as e:
            print(f"Error seeding sample data: {e}")
            return False