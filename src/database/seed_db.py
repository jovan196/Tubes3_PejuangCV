# seed_db.py
# Seeder script: if SQLite database doesn't exist or is empty, initialize from SQL dump and map resumes by round robin

import os
import sys
# Ensure src folder is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db_manager import DatabaseManager
from faker import Faker

# Paths
WORKSPACE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CV_BASE = os.path.join(WORKSPACE, 'data', 'cv')

def seed_dummy_data():
    fake = Faker()
    # Initialize DatabaseManager (creates tables)
    dbm = DatabaseManager()
    conn = dbm.connection
    cur = conn.cursor()

    # Check if any data exists
    cur.execute("SELECT COUNT(*) FROM ApplicantProfile")
    count = cur.fetchone()[0]
    if count > 0:
        print("Database already seeded.")
        return

    print("Seeding dummy data from data/cv folder using round-robin mapping...")
    # Build category -> pdf list mapping
    categories = [d for d in os.listdir(CV_BASE) if os.path.isdir(os.path.join(CV_BASE, d))]
    categories.sort()
    cat_files = {}
    max_len = 0
    for cat in categories:
        folder = os.path.join(CV_BASE, cat)
        pdfs = [f for f in os.listdir(folder) if f.lower().endswith('.pdf')]
        pdfs.sort()
        cat_files[cat] = pdfs
        if len(pdfs) > max_len:
            max_len = len(pdfs)
    # Create list of (cat, pdf) in round-robin
    pairs = []
    for i in range(max_len):
        for cat in categories:
            pdfs = cat_files.get(cat, [])
            if i < len(pdfs):
                pairs.append((cat, pdfs[i]))
    # Limit total seeded profiles
    MAX_PROFILES = 420
    pairs = pairs[:MAX_PROFILES]
    print(f"Total profiles to seed: {len(pairs)} (capped at {MAX_PROFILES})")
    # Seed for each pair
    for cat, pdf in pairs:
        # Generate realistic applicant info
        first_name = fake.first_name()
        last_name = fake.last_name()
        dob = fake.date_of_birth(minimum_age=18, maximum_age=60).isoformat()
        address = fake.address().replace("\n", ", ")
        phone_number = fake.phone_number()
        # Insert ApplicantProfile
        cur.execute(
            "INSERT INTO ApplicantProfile (first_name, last_name, date_of_birth, address, phone_number) VALUES (?, ?, ?, ?, ?)",
            (first_name, last_name, dob, address, phone_number)
        )
        applicant_id = cur.lastrowid
        # Construct cv_path relative to project root
        rel_path = os.path.join('data', 'cv', cat, pdf)
        # Insert ApplicationDetail with application_role = category
        cur.execute(
            "INSERT INTO ApplicationDetail (applicant_id, application_role, cv_path) VALUES (?, ?, ?)",
            (applicant_id, cat, rel_path)
        )
    conn.commit()
    conn.close()
    print("Seeding completed.")

if __name__ == '__main__':
    seed_dummy_data()
