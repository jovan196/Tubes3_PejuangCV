import mysql.connector
from mysql.connector import Error
import os
from typing import List, Dict, Optional
import csv
import re

class DatabaseManager:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 3306,
        user: str = "root",      # Username yang hardcoded untuk development
        password: str = "root",  # Password yang hardcoded buat development
        database: str = "ats_database"
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.is_pymysql = False  # Flag to track which connector is used
        
        try:
            # First try connecting with mysql-connector-python
            temp_connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                auth_plugin='mysql_native_password'
            )
            cursor = temp_connection.cursor()
            cursor.execute(f"DROP DATABASE IF EXISTS {self.database}") # Hapus database ats_database kalo ada
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}") # Bikin database ats_database yang baru
            temp_connection.commit()
            cursor.close()
            temp_connection.close()
            
            # Now connect to the database
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=False,
                auth_plugin='mysql_native_password'
            )
            print(f"Connected to MySQL/MariaDB database: {self.database}")
            self.create_tables()
            
        except Error as e:
            print(f"mysql-connector-python failed: {e}")
            # PyMySQL sebagai alternatif kalo mysql-connector-python gagal
            try:
                import pymysql
                pymysql.install_as_MySQLdb()
                
                # Create database if not exists
                temp_connection = pymysql.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password
                )
                cursor = temp_connection.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
                temp_connection.commit()
                cursor.close()
                temp_connection.close()
                
                # Connect to the database
                self.connection = pymysql.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    autocommit=False
                )
                self.is_pymysql = True  # Flag to use different cursor methods
                print(f"Connected to MariaDB using PyMySQL: {self.database}")
                self.create_tables()
                
            except Exception as e2:
                print(f"PyMySQL connection also failed: {e2}")
                # Try without auth_plugin for older MySQL/MariaDB versions
                try:
                    temp_connection = mysql.connector.connect(
                        host=self.host,
                        port=self.port,
                        user=self.user,
                        password=self.password
                    )
                    cursor = temp_connection.cursor()
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
                    temp_connection.commit()
                    cursor.close()
                    temp_connection.close()
                    
                    self.connection = mysql.connector.connect(
                        host=self.host,
                        port=self.port,
                        user=self.user,
                        password=self.password,
                        database=self.database,
                        autocommit=False
                    )
                    print(f"Connected to MySQL/MariaDB (no auth plugin): {self.database}")
                    self.create_tables()
                    
                except Error as e3:
                    print(f"All connection methods failed. Last error: {e3}")
                    raise e3
            print(f"Error connecting to MySQL: {e}")
            raise

    def disconnect(self) -> None:
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")    
    def create_tables(self) -> None:
        cursor = self.connection.cursor()
        
        # ApplicantProfile table (MySQL syntax)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ApplicantProfile (
                applicant_id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                date_of_birth DATE,
                address TEXT,
                phone_number VARCHAR(50)
            )
            """
        )
        
        # ApplicationDetail table (MySQL syntax)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ApplicationDetail (
                detail_id INT AUTO_INCREMENT PRIMARY KEY,
                applicant_id INT NOT NULL,
                application_role VARCHAR(200),
                cv_path TEXT,
                FOREIGN KEY (applicant_id) REFERENCES ApplicantProfile(applicant_id) ON DELETE CASCADE
            )
            """
        )
        
        self.connection.commit()
        print("Core tables (ApplicantProfile, ApplicationDetail) created successfully")

    def create_extracted_cv_table(self) -> None:
        """Create ExtractedCV table separately after seed data is loaded"""
        cursor = self.connection.cursor()
        
        # ExtractedCV table for fast searching
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ExtractedCV (
                id INT AUTO_INCREMENT PRIMARY KEY,
                cv_id VARCHAR(20) UNIQUE NOT NULL,
                resume_str LONGTEXT,
                resume_html LONGTEXT,
                category VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_cv_id (cv_id),
                INDEX idx_category (category),
                FULLTEXT(resume_str)
            )
            """
        )
        
        self.connection.commit()
        print("ExtractedCV table created successfully")

    def insert_applicant(self, first_name: str, last_name: str, date_of_birth: Optional[str] = None, address: str = "", phone_number: str = "") -> int:
        """
        Insert a new applicant into ApplicantProfile and return the new applicant_id.
        date_of_birth should be in 'YYYY-MM-DD' format or None.
        """
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO ApplicantProfile (first_name, last_name, date_of_birth, address, phone_number) VALUES (%s, %s, %s, %s, %s)",
            (first_name, last_name, date_of_birth, address, phone_number)
        )
        self.connection.commit()
        return cursor.lastrowid

    def insert_application(self, applicant_id: int, application_role: str, cv_path: str) -> int:
        """
        Insert a new application detail and return the new detail_id.
        """
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO ApplicationDetail (applicant_id, application_role, cv_path) VALUES (%s, %s, %s)",
            (applicant_id, application_role, cv_path)
        )
        self.connection.commit()
        return cursor.lastrowid

    def get_all_applications(self) -> List[Dict]:
        """
        Get all applications with applicant information.
        """
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT 
                ap.applicant_id, ap.first_name, ap.last_name, ap.date_of_birth, ap.address, ap.phone_number,
                ad.detail_id, ad.application_role, ad.cv_path
            FROM ApplicantProfile ap
            LEFT JOIN ApplicationDetail ad ON ap.applicant_id = ad.applicant_id
            """
        )
        return cursor.fetchall()

    def get_all_applicants(self) -> List[Dict]:
        """
        Get all applicant profiles.
        """
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ApplicantProfile")
        return cursor.fetchall()
    
    def import_csv_to_db(self, csv_file_path: str) -> None:
        """Import data from CSV to database"""
        try:
            with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    applicant_id = self.insert_applicant(
                        first_name=row.get('first_name', ''),
                        last_name=row.get('last_name', ''),
                        date_of_birth=row.get('date_of_birth'),
                        address=row.get('address', ''),
                        phone_number=row.get('phone_number', '')
                    )
                    
                    if row.get('application_role') or row.get('cv_path'):
                        self.insert_application(
                            applicant_id=applicant_id,
                            application_role=row.get('application_role', ''),
                            cv_path=row.get('cv_path', '')
                        )
            print(f"Successfully imported data from {csv_file_path}")
        except Exception as e:
            print(f"Error importing from CSV: {e}")

    def import_sql_file(self, sql_file_path: str) -> None:
        """Import data from SQL file to MySQL database"""
        try:
            with open(sql_file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Convert SQLite syntax to MySQL syntax
            sql_content = self.convert_sqlite_to_mysql(sql_content)
            
            # Split and execute SQL statements
            cursor = self.connection.cursor()
            
            # Split by semicolon and execute each statement
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            for statement in statements:
                if statement.upper().startswith(('INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP')):
                    try:
                        cursor.execute(statement)
                    except Error as e:
                        print(f"Warning: Skipping statement due to error: {e}")
                        print(f"Statement: {statement[:100]}...")
                        continue
            self.connection.commit()
            cursor.close()
            print(f"Successfully imported SQL from {sql_file_path}")
            
        except Exception as e:
            print(f"Error importing SQL file: {e}")
            self.connection.rollback()

    def convert_sqlite_to_mysql(self, sql_content: str) -> str:
        """Convert SQLite SQL syntax to MySQL syntax"""
        # Remove SQLite-specific commands
        sql_content = re.sub(r'BEGIN TRANSACTION;', '', sql_content)
        sql_content = re.sub(r'COMMIT;', '', sql_content)
        
        # Convert SQLite CREATE TABLE to MySQL
        sql_content = re.sub(r'INTEGER PRIMARY KEY AUTOINCREMENT', 'INT AUTO_INCREMENT PRIMARY KEY', sql_content)
        sql_content = re.sub(r'TEXT', 'VARCHAR(500)', sql_content)
        
        # Convert INSERT statements - remove double quotes around table names
        sql_content = re.sub(r'INSERT INTO "(\w+)"', r'INSERT INTO \1', sql_content)
          # Fix CV paths: convert single backslashes to forward slashes to prevent escape issues
        # This handles paths like 'data\cv\ACCOUNTANT\10554236.pdf'
        # The issue is that backslashes are being treated as escape characters
        sql_content = re.sub(r"'(data)\\(cv)\\([^\\]+)\\([^']+\.pdf)'", r"'data/cv/\3/\4'", sql_content)
        
        # Convert date format if needed
        sql_content = re.sub(r"'(\d{4}-\d{2}-\d{2})'", r"'\1'", sql_content)
        
        return sql_content

    # ExtractedCV methods
    def insert_extracted_cv(self, cv_id: str, resume_str: str, resume_html: str, category: str) -> None:
        """Insert extracted CV data"""
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT IGNORE INTO ExtractedCV (cv_id, resume_str, resume_html, category) VALUES (%s, %s, %s, %s)",
            (cv_id, resume_str, resume_html, category)
        )
        self.connection.commit()

    def get_all_extracted_cvs(self) -> List[Dict]:
        """Get all extracted CV data"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT cv_id, resume_str, resume_html, category FROM ExtractedCV")
            return cursor.fetchall()
        except Error as e:
            # Table might not exist yet
            if "doesn't exist" in str(e) or "Table" in str(e):
                return []
            else:
                raise e

    def import_extracted_cv_data(self, csv_file_path: str) -> None:
        """Import extracted CV data from CSV"""
        try:
            with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    self.insert_extracted_cv(
                        cv_id=row.get('ID', ''),
                        resume_str=row.get('Resume_str', ''),
                        resume_html=row.get('Resume_html', ''),
                        category=row.get('Category', '')
                    )
            print(f"Successfully imported extracted CV data from {csv_file_path}")
        except Exception as e:
            print(f"Error importing extracted CV data: {e}")

    def search_extracted_cvs(self, keywords: List[str], limit: Optional[int] = None) -> List[Dict]:
        """Search extracted CVs using keywords"""
        cursor = self.connection.cursor(dictionary=True)
        
        # Build WHERE clause for multiple keywords
        where_conditions = []
        params = []
        
        for keyword in keywords:
            where_conditions.append("(resume_str LIKE %s OR category LIKE %s)")
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        
        where_clause = " AND ".join(where_conditions)
        query = f"SELECT * FROM ExtractedCV WHERE {where_clause}"
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def get_cv_id_from_path(self, cv_path: Optional[str]) -> Optional[str]:
        """Extract CV ID from file path"""
        if cv_path is None or cv_path == '':
            return None
        match = re.search(r'(\d{8})\.pdf$', cv_path)
        return match.group(1) if match else None
