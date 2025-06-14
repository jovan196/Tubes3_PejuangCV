import re
from typing import List, Dict, Optional
from datetime import datetime

class RegexExtractor:
    def __init__(self):
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'(?:\+62|62|0)[\s-]?(?:\d{2,3})[\s-]?\d{3,4}[\s-]?\d{3,4}(?:[\s-]?\d{1,3})?')
        self.date_pattern = re.compile(r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}|\b\d{4}\b)\b')        
        self.skills_patterns = [
            # Programming Languages
            r'\b(?:Python|Java|JavaScript|TypeScript|C\+\+|C#|PHP|Ruby|Go|Rust|Kotlin|Swift|Scala|R|MATLAB|Perl|VBA|SQL)\b',
            # Web Technologies
            r'\b(?:HTML|CSS|React|Angular|Vue\.js|Node\.js|Express|Django|Flask|Spring|Laravel|ASP\.NET|Bootstrap|jQuery)\b',
            # Databases
            r'\b(?:MySQL|PostgreSQL|MongoDB|Redis|SQLite|Oracle|SQL Server|Cassandra|DynamoDB|Access)\b',
            # Cloud & DevOps
            r'\b(?:AWS|Azure|GCP|Docker|Kubernetes|Jenkins|Git|GitHub|GitLab|CI/CD|Terraform)\b',
            # Data Science & AI
            r'\b(?:TensorFlow|PyTorch|Pandas|NumPy|Scikit-learn|Keras|OpenCV|NLTK|Matplotlib|Seaborn|Tableau|Power BI)\b',
            # Mobile
            r'\b(?:Android|iOS|React Native|Flutter|Xamarin|Ionic)\b',
            # Design
            r'\b(?:Figma|Adobe XD|Photoshop|Illustrator|Sketch|InVision|Zeplin|Principle)\b',
            # Project Management & Methodologies
            r'\b(?:Agile|Scrum|Kanban|JIRA|Trello|Confluence|Slack|Asana|Waterfall|Lean)\b',
            # Testing & API
            r'\b(?:Selenium|Cypress|Jest|JUnit|PyTest|Postman|REST|GraphQL|API|SOAP)\b',
            # Operating Systems
            r'\b(?:Linux|Ubuntu|CentOS|Windows|macOS|Unix)\b',
            # Accounting & Finance specific skills
            r'\b(?:QuickBooks|SAP|Oracle|Peachtree|Excel|Sage|GAAP|IFRS|Financial Reporting|Accounts Payable|Accounts Receivable|General Ledger|Tax Preparation|Auditing|Budget|Forecasting|ERP)\b',
            # Microsoft Office
            r'\b(?:Microsoft Office|Excel|Word|PowerPoint|Outlook|Access|Microsoft|Office Suite)\b',
            # General Business Skills
            r'\b(?:Leadership|Management|Communication|Problem Solving|Team Work|Customer Service|Project Management|Strategic Planning|Analysis|Research)\b'        ]
        self.skills_pattern = re.compile('|'.join(self.skills_patterns), re.IGNORECASE)
        
        self.education_patterns = [
            # Degree patterns
            r'\b(?:S1|S2|S3|Sarjana|Master|Magister|Doktor|PhD|Bachelor|Graduate|Associate)\b.*?(?:Teknik Informatika|Computer Science|Sistem Informasi|Information Systems|Software Engineering|Data Science|Accounting|Business|Finance|Economics|Engineering)',
            # University patterns
            r'\b(?:Universitas|University|Institut|Institute|Politeknik|Polytechnic|Akademi|Academy|College)\s+[A-Za-z\s]+',
            # School patterns
            r'\b(?:SMA|SMK|High School)\s+[A-Za-z\s\d]+',
            # Year ranges with institutions
            r'\b\d{4}\s*[-–]\s*\d{4}\b.*?(?:Universitas|University|Institut|SMA|SMK|College)',
            # GPA patterns
            r'\b(?:GPA|IPK)\s*:?\s*\d{1}\.\d{1,2}',
            # Degree with year
            r'\b(?:Bachelor|Master|Associate|PhD|Doctorate)\s+(?:of\s+)?(?:Science|Arts|Business|Engineering).*?\d{4}',
        ]
        
        self.experience_patterns = [
            # Job titles with years
            r'(?:Software Engineer|Data Scientist|Frontend Developer|Backend Developer|Full Stack|DevOps|UI/UX Designer|Product Manager|Project Manager|Business Analyst|QA Engineer|Mobile Developer|Accountant|Financial Analyst|Controller|Manager|Director|Supervisor|Assistant|Clerk|Specialist).*?(?:\d{4}|\d{1,2}/\d{4})',
            # Year ranges with job
            r'\b\d{4}\s*[-–]\s*(?:\d{4}|present|now|sekarang|current)\b.*?(?:di|at|Company|Corp|Inc|LLC)\s+[A-Za-z\s&.,]+',
            # Experience duration
            r'(?:Pengalaman|Experience|Work|Kerja).*?(?:\d{1,2}\s*(?:tahun|years?|yr))',
            # Internship patterns
            r'(?:Intern|Magang|Trainee).*?(?:di|at)\s+[A-Za-z\s&.,]+',
            # Month Year to Month Year patterns
            r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\s+to\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}.*?[A-Z][a-z\s]+',
        ]
        
        self.summary_patterns = [
            # Standard summary sections
            r'(?:Summary|Ringkasan|Objective|Tujuan|Profile|Profil|About|Tentang)\s*:?\s*(.{50,1000}?)(?:\n\n|\r\n\r\n|(?=\b(?:Experience|Education|Skills|Highlights|Core|Professional)\b))',
            # Professional summary
            r'(?:Professional Summary|Career Objective|Personal Statement)\s*:?\s*(.{50,1000}?)(?:\n\n|\r\n\r\n|(?=\b(?:Experience|Education|Skills|Highlights|Core|Professional)\b))',
            # First paragraph that looks like a summary
            r'^([A-Z][^.!?]*[.!?]\s*[A-Z][^.!?]*[.!?].*?)(?:\n\n|\r\n\r\n|(?=\b(?:Experience|Education|Skills|Highlights|Core|Professional)\b))',
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
        lines = text.split('\n')[:10]  # Check more lines
        names = []
        
        # Pattern for full names (2-4 words, proper case)
        name_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}\b'
        
        # Skip lines that contain common CV keywords
        skip_keywords = ['curriculum', 'resume', 'cv', 'email', 'phone', 'address', 'summary', 
                        'experience', 'education', 'skills', 'objective', 'highlights', 'core',
                        'professional', 'accountant', 'engineer', 'developer', 'manager', 'company']
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or len(line) < 5:
                continue
                
            # Skip lines with common keywords
            if any(keyword in line.lower() for keyword in skip_keywords):
                continue
                
            # First few lines are more likely to contain names
            matches = re.findall(name_pattern, line)
            for match in matches:
                words = match.split()
                # Only accept if it's 2-4 words and not too long
                if 2 <= len(words) <= 4 and len(match) <= 50:
                    # Additional validation - shouldn't contain numbers or special chars
                    if not re.search(r'[\d@#$%^&*()_+\-=\[\]{};:"\\|,.<>?/]', match):
                        names.append(match.strip())
                        
        return list(set(names))  # Remove duplicates

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