import mysql.connector

def connect_to_db():
    # Fungsi untuk menghubungkan ke database MySQL
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="your_password",
        database="ats_db"
    )

def fetch_applicants():
    # Fungsi untuk mengambil data pelamar dari database
    db = connect_to_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ApplicantProfile")
    applicants = cursor.fetchall()
    db.close()
    return applicants

def fetch_applications():
    # Fungsi untuk mengambil data lamaran dari database
    db = connect_to_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ApplicationDetail")
    applications = cursor.fetchall()
    db.close()
    return applications