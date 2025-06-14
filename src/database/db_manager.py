import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Optional
import csv

class DatabaseManager:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 3306,
        user: str = "root",
        password: str = "",
        database: str = "ats_database"
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.connect()

    def connect(self) -> bool:
        try:
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
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=True
            )
            return True
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return False

    def disconnect(self) -> None:
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def create_tables(self) -> bool:
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS ApplicantProfile (
                applicant_id INT PRIMARY KEY AUTO_INCREMENT,
                full_name VARCHAR(255),
                email VARCHAR(255),
                phone VARCHAR(64),
                other_info TEXT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS ApplicationDetail (
                application_id INT PRIMARY KEY AUTO_INCREMENT,
                applicant_id INT,
                job_category VARCHAR(255),
                cv_path VARCHAR(512),
                resume_str LONGTEXT,
                resume_html LONGTEXT,
                FOREIGN KEY (applicant_id) REFERENCES ApplicantProfile(applicant_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            cursor.close()
            return True
        except Error as e:
            print(f"Error creating tables: {e}")
            return False

    def insert_applicant(self, name: str, email: str, phone: str, other_info: str = "") -> int:
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO ApplicantProfile (full_name, email, phone, other_info) VALUES (%s, %s, %s, %s)",
                (name, email, phone, other_info)
            )
            applicant_id = cursor.lastrowid
            cursor.close()
            return applicant_id
        except Error as e:
            print(f"Error inserting applicant: {e}")
            return -1

    def insert_application(self, applicant_id: int, category: str, cv_path: str, resume_str: str, resume_html: str) -> int:
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO ApplicationDetail (applicant_id, job_category, cv_path, resume_str, resume_html) VALUES (%s, %s, %s, %s, %s)",
                (applicant_id, category, cv_path, resume_str, resume_html)
            )
            application_id = cursor.lastrowid
            cursor.close()
            return application_id
        except Error as e:
            print(f"Error inserting application: {e}")
            return -1

    def get_all_applications(self) -> List[Dict]:
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("""
            SELECT ApplicationDetail.*, ApplicantProfile.full_name, ApplicantProfile.email, ApplicantProfile.phone
            FROM ApplicationDetail
            JOIN ApplicantProfile ON ApplicationDetail.applicant_id = ApplicantProfile.applicant_id
            """)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            print(f"Error getting all applications: {e}")
            return []

    def import_csv_to_db(self, csv_path: str) -> None:
        try:
            with open(csv_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    name = row.get('Name', f"Applicant_{row['ID']}")
                    email = row.get('Email', '')
                    phone = row.get('Phone', '')
                    other_info = ""
                    applicant_id = self.insert_applicant(name, email, phone, other_info)
                    cv_path = row.get('cv_path', f"data/{row['ID']}.pdf")
                    self.insert_application(
                        applicant_id,
                        row['Category'],
                        cv_path,
                        row['Resume_str'],
                        row['Resume_html']
                    )
        except Exception as e:
            print(f"Error importing CSV: {e}")

    def get_statistics(self) -> Dict:
        try:
            cursor = self.connection.cursor()
            stats = {}
            cursor.execute("SELECT COUNT(*) FROM ApplicationDetail")
            stats['total_applications'] = cursor.fetchone()[0]
            cursor.execute("SELECT job_category, COUNT(*) as count FROM ApplicationDetail GROUP BY job_category ORDER BY count DESC")
            stats['applications_by_category'] = cursor.fetchall()
            cursor.close()
            return stats
        except Error as e:
            print(f"Error getting statistics: {e}")
            return {}