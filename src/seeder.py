from faker import Faker
import random
import argparse


def generate_sql(num: int, out_path: str = '../data/seed_data.sql'):
    fake = Faker()
    roles = ['Software Engineer', 'Data Analyst', 'UI/UX Designer', 'HR Specialist', 'Backend Developer']

    with open(out_path, 'w', encoding='utf8') as f:
        # SQLite DDL
        f.write("""
-- Schema for SQLite
CREATE TABLE IF NOT EXISTS ApplicantProfile (
  applicant_id INTEGER PRIMARY KEY AUTOINCREMENT,
  first_name TEXT,
  last_name TEXT,
  date_of_birth DATE,
  address TEXT,
  phone_number TEXT
);

CREATE TABLE IF NOT EXISTS ApplicationDetail (
  detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
  applicant_id INTEGER NOT NULL,
  application_role TEXT,
  cv_path TEXT,
  FOREIGN KEY(applicant_id) REFERENCES ApplicantProfile(applicant_id)
);

""")
        f.write("BEGIN TRANSACTION;\n")
        # DML ApplicantProfile
        for _ in range(num):
            first = fake.first_name().replace("'", "''")
            last = fake.last_name().replace("'", "''")
            dob = fake.date_of_birth(minimum_age=18, maximum_age=60).strftime('%Y-%m-%d')
            addr = fake.address().replace("'", "''").replace("\n", ", ")
            phone = fake.phone_number().replace("'", "''")
            f.write(f"INSERT INTO ApplicantProfile (first_name, last_name, date_of_birth, address, phone_number) VALUES ('{first}','{last}','{dob}','{addr}','{phone}');\n")
        # DML ApplicationDetail
        for i in range(1, num+1):
            role = random.choice(roles)
            cv = f"../data/{fake.uuid4()}.pdf"
            f.write(f"INSERT INTO ApplicationDetail (applicant_id, application_role, cv_path) VALUES ({i},'{role}','{cv}');\n")
        f.write("COMMIT;\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate SQL seed file for ATS SQLite database')
    parser.add_argument('--num', type=int, default=100, help='Number of applicants to generate')
    parser.add_argument('--out', type=str, default='../data/seed_data.sql', help='Output SQL file path')
    args = parser.parse_args()
    generate_sql(args.num, args.out)
    print(f"Generated {args.out} with {args.num} applicants.")