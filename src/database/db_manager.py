import sqlite3
import os
from typing import List, Dict, Optional
import csv

class DatabaseManager:
    def __init__(
        self,
        db_path: str = None
    ):
        # Determine database file path
        if not db_path:
            # default to ats.db in workspace root
            db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'ats.db'))
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        # Connect to SQLite
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.create_tables()

    def disconnect(self) -> None:
        if self.connection:
            self.connection.close()

    def create_tables(self) -> None:
        cursor = self.connection.cursor()
        # ApplicantProfile according to provided model
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ApplicantProfile (
                applicant_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT,
                last_name TEXT,
                date_of_birth TEXT,
                address TEXT,
                phone_number TEXT
            )
            """
        )
        # ApplicationDetail according to provided model
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ApplicationDetail (
                detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
                applicant_id INTEGER NOT NULL,
                application_role TEXT,
                cv_path TEXT,
                FOREIGN KEY (applicant_id) REFERENCES ApplicantProfile(applicant_id)
            )
            """
        )
        
        # ExtractedCV table for quick search
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ExtractedCV (
                cv_id TEXT PRIMARY KEY,
                resume_str TEXT,
                resume_html TEXT,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.connection.commit()

    def insert_applicant(self, first_name: str, last_name: str, date_of_birth: Optional[str] = None, address: str = "", phone_number: str = "") -> int:
        """
        Insert a new applicant into ApplicantProfile and return the new applicant_id.
        date_of_birth should be in 'YYYY-MM-DD' format or None.
        """
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO ApplicantProfile (first_name, last_name, date_of_birth, address, phone_number) VALUES (?, ?, ?, ?, ?)",
            (first_name, last_name, date_of_birth, address, phone_number)
        )
        self.connection.commit()
        return cursor.lastrowid

    def insert_application(self, applicant_id: int, application_role: Optional[str], cv_path: str) -> int:
        """
        Insert a new application detail row and return the new detail_id.
        application_role can be None.
        """
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO ApplicationDetail (applicant_id, application_role, cv_path) VALUES (?, ?, ?)",
            (applicant_id, application_role, cv_path)
        )
        self.connection.commit()
        return cursor.lastrowid

    def get_all_applications(self) -> List[Dict]:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT
                AP.applicant_id,
                AP.first_name,
                AP.last_name,
                AP.date_of_birth,
                AP.address,
                AP.phone_number,
                AD.detail_id,
                AD.application_role,
                AD.cv_path
            FROM ApplicantProfile AP
            JOIN ApplicationDetail AD ON AP.applicant_id = AD.applicant_id
            """
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def import_csv_to_db(self, csv_path: str) -> None:
        try:
            with open(csv_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    full_name = row.get('Name', f"Applicant_{row['ID']}")
                    parts = full_name.split()
                    first_name = parts[0] if parts else ''
                    last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
                    # CSV may not contain date_of_birth/address/phone, leave empty
                    applicant_id = self.insert_applicant(first_name, last_name)
        except Exception as e:
            print(f"Error importing CSV: {e}")

    def import_extracted_cv_data(self, csv_path: str) -> None:
        """Import extracted CV data from CSV"""
        if not os.path.exists(csv_path):
            print(f"CSV file not found: {csv_path}")
            return
        
        cursor = self.connection.cursor()
        
        # Clear existing extracted CV data
        cursor.execute("DELETE FROM ExtractedCV")
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                cursor.execute(
                    """
                    INSERT INTO ExtractedCV (cv_id, resume_str, resume_html, category)
                    VALUES (?, ?, ?, ?)
                    """,
                    (row['ID'], row['Resume_str'], row['Resume_html'], row['Category'])
                )
        
        self.connection.commit()
        print(f"Imported extracted CV data from {csv_path}")
    
    def get_extracted_cv_by_id(self, cv_id: str) -> Optional[Dict]:
        """Get extracted CV data by ID"""
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT * FROM ExtractedCV WHERE cv_id = ?",
            (cv_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_all_extracted_cvs(self) -> List[Dict]:
        """Get all extracted CVs"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM ExtractedCV")
        return [dict(row) for row in cursor.fetchall()]
    
    def search_extracted_cvs(self, keywords: List[str], limit: int = None) -> List[Dict]:
        """Search extracted CVs by keywords"""
        cursor = self.connection.cursor()
        
        # Build search query with LIKE operators for each keyword
        where_conditions = []
        params = []
        
        for keyword in keywords:
            where_conditions.append("(resume_str LIKE ? OR category LIKE ?)")
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        
        where_clause = " AND ".join(where_conditions)
        query = f"SELECT * FROM ExtractedCV WHERE {where_clause}"
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_cv_id_from_path(self, cv_path: str) -> Optional[str]:
        """Extract CV ID from file path"""
        import re
        match = re.search(r'(\d{8})\.pdf$', cv_path)
        return match.group(1) if match else None
