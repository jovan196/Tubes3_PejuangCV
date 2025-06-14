import re
from typing import List, Dict, Optional
from datetime import datetime

class RegexExtractor:
    def __init__(self):
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'(?:\+62|62|0)[\s-]?(?:\d{2,3})[\s-]?\d{3,4}[\s-]?\d{3,4}(?:[\s-]?\d{1,3})?')
        self.date_pattern = re.compile(r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}|\b\d{4}\b)\b')
        self.skills_patterns = [
            r'\b(?:Python|Java|JavaScript|TypeScript|C\+\+|C#|PHP|Ruby|Go|Rust|Kotlin|Swift|Scala|R|MATLAB|Perl)\b',
            r'\b(?:HTML|CSS|React|Angular|Vue\.js|Node\.js|Express|Django|Flask|Spring|Laravel|ASP\.NET)\b',
            r'\b(?:MySQL|PostgreSQL|MongoDB|Redis|SQLite|Oracle|SQL Server|Cassandra|DynamoDB)\b',
            r'\b(?:AWS|Azure|GCP|Docker|Kubernetes|Jenkins|Git|GitHub|GitLab|CI/CD|Terraform)\b',
            r'\b(?:TensorFlow|PyTorch|Pandas|NumPy|Scikit-learn|Keras|OpenCV|NLTK|Matplotlib|Seaborn)\b',
            r'\b(?:Android|iOS|React Native|Flutter|Xamarin|Ionic)\b',
            r'\b(?:Figma|Adobe XD|Photoshop|Illustrator|Sketch|InVision|Zeplin|Principle)\b',
            r'\b(?:Agile|Scrum|Kanban|JIRA|Trello|Confluence|Slack|Asana)\b',
            r'\b(?:Selenium|Cypress|Jest|JUnit|PyTest|Postman|REST|GraphQL|API)\b',
            r'\b(?:Linux|Ubuntu|CentOS|Windows|macOS|Unix)\b'
        ]
        self.skills_pattern = re.compile('|'.join(self.skills_patterns), re.IGNORECASE)
        self.education_patterns = [
            r'\b(?:S1|S2|S3|Sarjana|Master|Magister|Doktor|PhD|Bachelor|Graduate)\b.*?(?:Teknik Informatika|Computer Science|Sistem Informasi|Information Systems|Software Engineering|Data Science)',
            r'\b(?:Universitas|University|Institut|Institute|Politeknik|Polytechnic|Akademi|Academy)\s+[A-Za-z\s]+',
            r'\b(?:SMA|SMK|High School)\s+[A-Za-z\s\d]+',
            r'\b\d{4}\s*[-–]\s*\d{4}\b.*?(?:Universitas|University|Institut|SMA|SMK)',
            r'\b(?:GPA|IPK)\s*:?\s*\d{1}\.\d{1,2}',
        ]
        self.experience_patterns = [
            r'(?:Software Engineer|Data Scientist|Frontend Developer|Backend Developer|Full Stack|DevOps|UI/UX Designer|Product Manager|Project Manager|Business Analyst|QA Engineer|Mobile Developer).*?(?:\d{4}|\d{1,2}/\d{4})',
            r'\b\d{4}\s*[-–]\s*(?:\d{4}|present|now|sekarang)\b.*?(?:di|at)\s+[A-Za-z\s&.,]+',
            r'(?:Pengalaman|Experience|Work|Kerja).*?(?:\d{1,2}\s*tahun|\d{1,2}\s*years?)',
            r'(?:Intern|Magang|Trainee).*?(?:di|at)\s+[A-Za-z\s&.,]+',
        ]
        self.summary_patterns = [
            r'(?:Summary|Ringkasan|Objective|Tujuan|Profile|Profil|About|Tentang)\s*:?\s*(.{50,500})',
            r'(?:Professional Summary|Career Objective|Personal Statement)\s*:?\s*(.{50,500})',
        ]

    def extract_emails(self, text: str):
        emails = self.email_pattern.findall(text)
        return list(set(emails))

    def extract_phone_numbers(self, text: str):
        phones = self.phone_pattern.findall(text)
        cleaned_phones = []
        for phone in phones:
            clean_phone = re.sub(r'[\s-]', '', phone)
            cleaned_phones.append(clean_phone)
        return list(set(cleaned_phones))

    def extract_skills(self, text: str):
        skills = self.skills_pattern.findall(text)
        cleaned_skills = []
        for skill in skills:
            if skill and skill.strip():
                cleaned_skills.append(skill.strip())
        return list(set(cleaned_skills))

    def extract_education(self, text: str):
        education_info = []
        for pattern in self.education_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if isinstance(match, tuple):
                    match = ' '.join(match)
                if match.strip() and len(match.strip()) > 5:
                    education_info.append(match.strip())
        return list(set(education_info))

    def extract_experience(self, text: str):
        experience_info = []
        for pattern in self.experience_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if isinstance(match, tuple):
                    match = ' '.join(match)
                if match.strip() and len(match.strip()) > 10:
                    experience_info.append(match.strip())
        return list(set(experience_info))

    def extract_summary(self, text: str):
        summaries = []
        for pattern in self.summary_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            for match in matches:
                if isinstance(match, tuple):
                    match = ' '.join(match)
                if match.strip() and len(match.strip()) > 20:
                    clean_summary = re.sub(r'\s+', ' ', match.strip())
                    summaries.append(clean_summary)
        return summaries

    def extract_dates(self, text: str):
        dates = self.date_pattern.findall(text)
        return list(set(dates))

    def extract_names(self, text: str):
        lines = text.split('\n')[:5]
        names = []
        name_pattern = r'\b[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b'
        for line in lines:
            if any(keyword in line.lower() for keyword in ['curriculum', 'resume', 'cv', 'email', 'phone', 'address']):
                continue
            matches = re.findall(name_pattern, line)
            for match in matches:
                if len(match.split()) >= 2:
                    names.append(match.strip())
        return names

    def extract_cv_info(self, text: str):
        if not text or len(text.strip()) < 50:
            return {
                'emails': [],
                'phones': [],
                'skills': [],
                'education': [],
                'experience': [],
                'summary': [],
                'dates': [],
                'names': []
            }
        return {
            'emails': self.extract_emails(text),
            'phones': self.extract_phone_numbers(text),
            'skills': self.extract_skills(text),
            'education': self.extract_education(text),
            'experience': self.extract_experience(text),
            'summary': self.extract_summary(text),
            'dates': self.extract_dates(text),
            'names': self.extract_names(text)
        }