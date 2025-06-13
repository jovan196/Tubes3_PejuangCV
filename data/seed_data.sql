
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

BEGIN TRANSACTION;
INSERT INTO ApplicantProfile (first_name, last_name, date_of_birth, address, phone_number) VALUES ('Daniel','Gonzalez','1987-01-10','PSC 6870, Box 4208, APO AA 77653','4034707125');
INSERT INTO ApplicantProfile (first_name, last_name, date_of_birth, address, phone_number) VALUES ('Amanda','Wilson','2005-04-16','7119 Gabriela Camp Suite 257, Lake Amber, VI 97461','832-585-7102x7827');
INSERT INTO ApplicantProfile (first_name, last_name, date_of_birth, address, phone_number) VALUES ('Stephen','Cooper','1977-11-19','544 Andrew Passage Suite 032, South Jesse, CA 54274','(400)291-7409x53618');
INSERT INTO ApplicantProfile (first_name, last_name, date_of_birth, address, phone_number) VALUES ('Joshua','Farmer','1983-07-17','0811 Terri Greens Suite 352, Port Kylehaven, NE 53525','001-537-580-4728x88730');
INSERT INTO ApplicantProfile (first_name, last_name, date_of_birth, address, phone_number) VALUES ('Eugene','Jackson','1995-04-02','8258 Joshua Brook Suite 895, Caldwellburgh, WI 65675','3414946426');
INSERT INTO ApplicationDetail (applicant_id, application_role, cv_path) VALUES (1,'Software Engineer','../data/cbe7c311-4b84-4c27-b3fc-91bacefbed59.pdf');
INSERT INTO ApplicationDetail (applicant_id, application_role, cv_path) VALUES (2,'HR Specialist','../data/b4af6f9f-344c-41bd-9c4c-8cc31e6f0489.pdf');
INSERT INTO ApplicationDetail (applicant_id, application_role, cv_path) VALUES (3,'Software Engineer','../data/6c72d9b7-092e-4ed0-9e15-51553d24efd7.pdf');
INSERT INTO ApplicationDetail (applicant_id, application_role, cv_path) VALUES (4,'Software Engineer','../data/361a4d2a-3b81-47b8-a2ad-93c9868906f6.pdf');
INSERT INTO ApplicationDetail (applicant_id, application_role, cv_path) VALUES (5,'Backend Developer','../data/5d0f6849-0fb1-48f8-ad4a-204fb33d8528.pdf');
COMMIT;
