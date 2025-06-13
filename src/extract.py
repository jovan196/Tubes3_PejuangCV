import re
import pdfplumber
from typing import Dict, List, Optional
from datetime import datetime
from db import get_engine, init_db, get_session, ApplicantProfile, ApplicationDetail

# Enhanced regex patterns for ATS CVs
EMAIL_REGEX = re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b')
PHONE_REGEX = re.compile(r'(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})|(?:\+\d{1,3}[-.\s]?)?(?:\d{1,4}[-.\s]?){1,4}\d{1,4}')
# Enhanced date patterns for ATS format
DATE_REGEX = re.compile(r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2}|\w+\s+\d{4})\b')
# More comprehensive heading patterns for ATS CVs
HEADING_REGEX = re.compile(r'^(?:PERSONAL\s+INFORMATION|CONTACT\s+INFORMATION|SUMMARY|OBJECTIVE|PROFILE|SKILLS|TECHNICAL\s+SKILLS|CORE\s+COMPETENCIES|HIGHLIGHTS|ACCOMPLISHMENTS|ACHIEVEMENTS|WORK\s+EXPERIENCE|PROFESSIONAL\s+EXPERIENCE|EXPERIENCE|EMPLOYMENT\s+HISTORY|EDUCATION|ACADEMIC\s+BACKGROUND|CERTIFICATIONS|LICENSES|PROJECTS|LANGUAGES|REFERENCES|AWARDS|PUBLICATIONS|VOLUNTEER\s+EXPERIENCE):?', 
                           re.IGNORECASE | re.MULTILINE)
# Enhanced date range patterns for various ATS formats
DATE_RANGE_REGEX = re.compile(r'(?P<start>(?:\d{1,2}\/\d{4}|\d{4}|\w+\s+\d{4}))\s*[-–—]\s*(?P<end>(?:\d{1,2}\/\d{4}|\d{4}|\w+\s+\d{4}|Present|Current|Now))', re.IGNORECASE)
# Name extraction pattern (typically at the beginning)
NAME_REGEX = re.compile(r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]*)*)\s*$', re.MULTILINE)
# Location/Address pattern
LOCATION_REGEX = re.compile(r'(?:[A-Z][a-z]+,?\s*[A-Z]{2}(?:\s+\d{5})?|[A-Z][a-z]+,?\s*[A-Z][a-z]+(?:,?\s*[A-Z]{2})?)')
# LinkedIn profile pattern
LINKEDIN_REGEX = re.compile(r'(?:linkedin\.com/in/|linkedin\.com/pub/)([a-zA-Z0-9-]+)', re.IGNORECASE)


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Convert a PDF file to its full text string using pdfplumber with ATS optimization.
    """
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                # Try different extraction methods for better ATS compatibility
                page_text = page.extract_text(
                    x_tolerance=1,      # Tighter tolerance for better line breaks
                    y_tolerance=1,      # Tighter tolerance for better line breaks
                    layout=True,        # Preserve layout
                    keep_blank_chars=False,
                    use_text_flow=False  # Don't follow text flow to preserve structure
                )
                
                # Fallback to table extraction if text extraction fails
                if not page_text or len(page_text.strip()) < 10:
                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            for row in table:
                                if row:
                                    page_text += " ".join([cell for cell in row if cell]) + "\n"
                
                if page_text:
                    text += page_text + "\n"
                    
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""
    
    # Post-process the entire text with improved normalization
    text = normalize_text_improved(text)
    return text


def normalize_text_improved(text: str) -> str:
    """
    Improved text normalization for better structure preservation.
    """
    # Remove excessive whitespace but preserve line breaks
    text = re.sub(r'[ \t]+', ' ', text)  # Normalize spaces and tabs
    text = re.sub(r'\n[ \t]+', '\n', text)  # Remove leading spaces after newlines
    text = re.sub(r'[ \t]+\n', '\n', text)  # Remove trailing spaces before newlines
    text = re.sub(r'\n{3,}', '\n\n', text)  # Limit consecutive newlines to 2
    
    # Fix common encoding issues
    text = text.replace('ï¼​', ' - ')  # Replace special characters
    text = text.replace('–', '-')  # Replace en-dash with hyphen
    text = text.replace('—', '-')  # Replace em-dash with hyphen
    
    return text.strip()


def normalize_text(text: str) -> str:
    """
    Legacy normalize function - keeping for compatibility.
    """
    return normalize_text_improved(text)


def parse_sections(text: str) -> Dict[str, str]:
    """
    Split the document into sections by headings with enhanced ATS support.
    """
    sections: Dict[str, str] = {}
    
    # Define section keywords and their standard names
    section_keywords = {
        'skills': ['Skills', 'SKILLS', 'Technical Skills', 'Core Competencies'],
        'summary': ['Summary', 'SUMMARY', 'Profile', 'Objective', 'Professional Summary'],
        'highlights': ['Highlights', 'HIGHLIGHTS', 'Key Qualifications', 'Accomplishments'],
        'accomplishments': ['Accomplishments', 'ACCOMPLISHMENTS', 'Achievements', 'Awards'],
        'experience': ['Experience', 'EXPERIENCE', 'Work Experience', 'Professional Experience', 'Employment History'],
        'education': ['Education', 'EDUCATION', 'Academic Background', 'Educational Background']
    }
    
    lines = text.split('\n')
    current_section = None
    current_content = []
    
    for line in lines:
        line = line.strip()
        if not line:
            if current_content:
                current_content.append('')  # Preserve empty lines within sections
            continue
        
        # Check if this line is a section header
        is_section_header = False
        for section_name, keywords in section_keywords.items():
            if any(line == keyword or line.startswith(keyword) for keyword in keywords):
                # Save previous section
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = section_name
                current_content = []
                is_section_header = True
                break
        
        if not is_section_header:
            current_content.append(line)
    
    # Save the last section
    if current_section and current_content:
        sections[current_section] = '\n'.join(current_content).strip()
    
    return sections


def normalize_section_key(heading: str) -> str:
    """
    Normalize section headings to standard keys.
    """
    heading = heading.lower().strip().rstrip(':')
    
    # Map various heading formats to standard keys
    mapping = {
        'personal information': 'personal',
        'contact information': 'contact',
        'objective': 'summary',
        'profile': 'summary',
        'technical skills': 'skills',
        'core competencies': 'skills',
        'work experience': 'experience',
        'professional experience': 'experience',
        'employment history': 'experience',
        'academic background': 'education',
        'volunteer experience': 'volunteer'
    }
    
    return mapping.get(heading, heading)


def parse_experience_entries(text: str) -> List[Dict[str, str]]:
    """
    Parse multiple experience blocks into structured entries with enhanced ATS support.
    """
    entries: List[Dict[str, str]] = []
    
    if not text.strip():
        return entries
    
    # Split by date patterns - look for MM/YYYY - MM/YYYY format
    date_pattern = r'(\d{2}/\d{4}\s*-\s*\d{2}/\d{4})'
    parts = re.split(date_pattern, text)
    
    i = 0
    while i < len(parts):
        if i + 1 < len(parts) and re.match(date_pattern, parts[i]):
            # Found a date range
            date_range = parts[i].strip()
            content = parts[i + 1].strip() if i + 1 < len(parts) else ""
            
            # Parse date range
            dates = re.search(r'(\d{2}/\d{4})\s*-\s*(\d{2}/\d{4})', date_range)
            if dates:
                start_date = dates.group(1)
                end_date = dates.group(2)
                
                # Parse content
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                
                if lines:
                    # First line usually contains company and position
                    first_line = lines[0]
                    
                    # Extract company name and position
                    company = ""
                    title = ""
                    location = ""
                    
                    # Look for "Company Name - City, State Position"
                    company_match = re.search(r'^(.+?)\s+-\s+(.+?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*$', first_line)
                    if company_match:
                        company = company_match.group(1).strip()
                        location = company_match.group(2).strip()
                        title = company_match.group(3).strip()
                    else:
                        # Fallback: treat the whole line as company info
                        company = first_line
                    
                    # Description is the remaining lines
                    description_lines = lines[1:] if len(lines) > 1 else []
                    description = '\n'.join(description_lines)
                    
                    entry = {
                        'start': start_date,
                        'end': end_date,
                        'company': company,
                        'title': title,
                        'location': location,
                        'description': description
                    }
                    
                    entries.append(entry)
            
            i += 2  # Skip both date and content parts
        else:
            i += 1
    
    return entries


def normalize_date(date_str: str) -> str:
    """
    Normalize various date formats to a consistent format.
    """
    date_str = date_str.strip()
    
    # Handle common ATS date formats
    if re.match(r'^\d{4}$', date_str):
        return date_str
    elif re.match(r'^\d{1,2}/\d{4}$', date_str):
        return date_str
    elif date_str.lower() in ['present', 'current', 'now']:
        return 'Present'
    elif re.match(r'^\w+\s+\d{4}$', date_str):
        # Convert "January 2023" to "01/2023"
        month_map = {
            'january': '01', 'february': '02', 'march': '03', 'april': '04',
            'may': '05', 'june': '06', 'july': '07', 'august': '08',
            'september': '09', 'october': '10', 'november': '11', 'december': '12'
        }
        parts = date_str.lower().split()
        if len(parts) == 2 and parts[0] in month_map:
            return f"{month_map[parts[0]]}/{parts[1]}"
    
    return date_str


def parse_education_entries(text: str) -> List[Dict[str, str]]:
    """
    Parse education section into structured entries with enhanced ATS support.
    """
    entries: List[Dict[str, str]] = []
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    
    if not lines:
        return entries
    
    current_entry = {
        'year': '',
        'degree': '',
        'institution': '',
        'details': ''
    }
    
    for i, line in enumerate(lines):
        # Check if line starts with a year
        if re.match(r'^\d{4}$', line):
            # Save previous entry if it has content
            if current_entry['year'] or current_entry['degree'] or current_entry['institution']:
                entries.append(current_entry)
            
            # Start new entry
            current_entry = {
                'year': line,
                'degree': '',
                'institution': '',
                'details': ''
            }
        elif current_entry['year']:  # We have a year, so this line belongs to current entry
            # Check if this line contains institution info
            if any(keyword in line for keyword in ['University', 'College', 'School', 'Institute', 'Academy', 'Tech']):
                # Extract institution and any degree info
                degree_keywords = ['Diploma', 'Bachelor', 'Master', 'PhD', 'Certificate', 'BS', 'BA', 'MS', 'MA', 'MBA']
                
                for keyword in degree_keywords:
                    if keyword in line:
                        # Split around the degree keyword
                        parts = line.split(keyword)
                        if len(parts) >= 2:
                            current_entry['institution'] = parts[0].strip()
                            current_entry['degree'] = keyword + parts[1].split(':')[0].strip()
                            # Any remaining part goes to details
                            if ':' in parts[1]:
                                current_entry['details'] = ':'.join(parts[1].split(':')[1:]).strip()
                        break
                else:
                    # No degree keyword found, treat as institution
                    if not current_entry['institution']:
                        current_entry['institution'] = line
                    else:
                        current_entry['details'] = current_entry['details'] + '\n' + line if current_entry['details'] else line
            else:
                # Add to details
                current_entry['details'] = current_entry['details'] + '\n' + line if current_entry['details'] else line
    
    # Add the last entry
    if current_entry['year'] or current_entry['degree'] or current_entry['institution']:
        entries.append(current_entry)
    
    return entries


def extract_name(text: str) -> str:
    """
    Extract the candidate's name from the CV text.
    """
    lines = text.split('\n')[:10]  # Check first 10 lines
    
    for line in lines:
        line = line.strip()
        # Skip common headers and numbers
        if any(header in line.lower() for header in ['resume', 'curriculum vitae', 'cv', 'email', 'phone', 'skills', 'summary']):
            continue
        
        # Skip single numbers or very short lines
        if len(line) < 3 or line.isdigit():
            continue
        
        # Look for name patterns - typically 2-4 words, starting with capital letters
        name_match = re.match(r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]*){1,3})\s*$', line)
        if name_match:
            potential_name = name_match.group(1).strip()
            # Avoid common job titles or positions
            if not any(title in potential_name.lower() for title in ['chef', 'cook', 'manager', 'director', 'assistant', 'food', 'prep']):
                return potential_name
    
    return ""


def extract_contact_info(text: str) -> Dict[str, str]:
    """
    Extract contact information from CV text.
    """
    contact = {
        'email': '',
        'phone': '',
        'linkedin': '',
        'location': ''
    }
    
    # Extract email
    email_matches = EMAIL_REGEX.findall(text)
    if email_matches:
        contact['email'] = email_matches[0]
    
    # Extract phone
    phone_matches = PHONE_REGEX.findall(text)
    if phone_matches:
        if isinstance(phone_matches[0], tuple):
            phone = ''.join(phone_matches[0])
        else:
            phone = phone_matches[0]
        contact['phone'] = phone
    
    # Extract LinkedIn
    linkedin_matches = LINKEDIN_REGEX.findall(text)
    if linkedin_matches:
        contact['linkedin'] = f"linkedin.com/in/{linkedin_matches[0]}"
    
    # Extract location (look in first part of document)
    location_match = LOCATION_REGEX.search(text[:500])
    if location_match:
        contact['location'] = location_match.group(0).strip()
    
    return contact


def extract_info(text: str) -> Dict[str, object]:
    """
    Extract structured info from CV text with enhanced ATS support.
    """
    info: Dict[str, object] = {}
    
    # Basic pattern extraction
    info['emails'] = EMAIL_REGEX.findall(text)
    info['phones'] = PHONE_REGEX.findall(text)
    info['dates'] = DATE_REGEX.findall(text)
    
    # Enhanced extractions
    info['name'] = extract_name(text)
    info['contact'] = extract_contact_info(text)
    
    # Parse sections
    secs = parse_sections(text)
    
    # Standard sections
    info['summary'] = secs.get('summary', '')
    info['skills'] = parse_skills_section(secs.get('skills', ''))
    info['highlights'] = secs.get('highlights', '')
    info['accomplishments'] = secs.get('accomplishments', '')
    
    # Enhanced parsing for experience and education
    info['experience_entries'] = parse_experience_entries(secs.get('experience', ''))
    info['education_entries'] = parse_education_entries(secs.get('education', ''))
    
    # Additional ATS sections
    info['certifications'] = secs.get('certifications', '')
    info['projects'] = secs.get('projects', '')
    info['languages'] = secs.get('languages', '')
    info['volunteer'] = secs.get('volunteer', '')
    
    # Extract years of experience
    info['years_of_experience'] = calculate_years_of_experience(info['experience_entries'])
    
    return info


def parse_skills_section(skills_text: str) -> List[str]:
    """
    Parse skills section with better handling of ATS formats and lists.
    """
    if not skills_text:
        return []
    
    skills = []
    lines = [line.strip() for line in skills_text.split('\n') if line.strip()]
    
    for line in lines:
        # Skip empty lines
        if not line:
            continue
            
        # Handle bullet points and various list formats
        line = re.sub(r'^[-•◦▪▫▸▹►▻⁃⁌⁍]+\s*', '', line)  # Remove bullet points
        line = re.sub(r'^\d+\.?\s*', '', line)  # Remove numbered list markers
        
        # Split by common delimiters within the line
        if any(delimiter in line for delimiter in [';', ',', '|']):
            for delimiter in [';', ',', '|']:
                if delimiter in line:
                    line_skills = [s.strip() for s in line.split(delimiter) if s.strip()]
                    skills.extend(line_skills)
                    break
        else:
            # Treat each line as a separate skill
            if len(line) > 1:  # Avoid single characters
                skills.append(line)
    
    # Clean and deduplicate
    cleaned_skills = []
    for skill in skills:
        skill = skill.strip()
        if skill and len(skill) > 1 and skill not in cleaned_skills:
            cleaned_skills.append(skill)
    
    return cleaned_skills


def calculate_years_of_experience(experience_entries: List[Dict[str, str]]) -> Optional[int]:
    """
    Calculate total years of experience from experience entries.
    """
    if not experience_entries:
        return None
    
    total_months = 0
    current_year = 2025  # Current year
    
    for entry in experience_entries:
        start_date = entry.get('start', '')
        end_date = entry.get('end', '')
        
        if not start_date:
            continue
        
        try:
            # Parse start date
            if '/' in start_date:
                start_month, start_year = map(int, start_date.split('/'))
            elif start_date.isdigit() and len(start_date) == 4:
                start_year, start_month = int(start_date), 1
            else:
                continue
            
            # Parse end date
            if end_date.lower() in ['present', 'current', 'now']:
                end_year, end_month = current_year, 12
            elif '/' in end_date:
                end_month, end_year = map(int, end_date.split('/'))
            elif end_date.isdigit() and len(end_date) == 4:
                end_year, end_month = int(end_date), 12
            else:
                continue
            
            # Calculate duration in months
            duration = (end_year - start_year) * 12 + (end_month - start_month)
            total_months += max(0, duration)
            
        except (ValueError, AttributeError):
            continue
    
    return max(0, total_months // 12) if total_months > 0 else None


def save_to_database(extracted_info: Dict[str, object], cv_path: str = None, application_role: str = None) -> bool:
    """
    Save extracted CV information to the database.
    Returns True if successful, False otherwise.
    """
    try:
        # Initialize database
        engine = get_engine()
        init_db(engine)
        session = get_session(engine)
        
        # Extract contact information
        contact = extracted_info.get('contact', {})
        name = extracted_info.get('name', '')
        
        # Parse name into first and last name
        name_parts = name.split() if name else []
        first_name = name_parts[0] if name_parts else None
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else None
        
        # Extract phone and format it
        phone = contact.get('phone', '')
        if isinstance(phone, tuple):
            phone = ''.join(phone)
        
        # Create ApplicantProfile
        profile = ApplicantProfile(
            first_name=first_name,
            last_name=last_name,
            address=contact.get('location', None),
            phone_number=phone if phone else None
        )
        
        session.add(profile)
        session.flush()  # Get the ID
        
        # Create ApplicationDetail
        application = ApplicationDetail(
            applicant_id=profile.applicant_id,
            application_role=application_role,
            cv_path=cv_path
        )
        
        session.add(application)
        session.commit()
        
        print(f"✅ Successfully saved to database with ID: {profile.applicant_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving to database: {e}")
        if 'session' in locals():
            session.rollback()
        return False
    finally:
        if 'session' in locals():
            session.close()


def display_extracted_info_formatted(parsed_info: Dict[str, object]) -> None:
    """
    Display extracted information in a well-formatted, readable way.
    """
    print("\n" + "=" * 60)
    print("📋 FORMATTED CV EXTRACTION RESULTS")
    print("=" * 60)
    
    # Basic Information
    if parsed_info.get('name'):
        print(f"👤 NAME: {parsed_info['name']}")
    
    contact = parsed_info.get('contact', {})
    if contact.get('email'):
        print(f"📧 EMAIL: {contact['email']}")
    if contact.get('phone'):
        print(f"📞 PHONE: {contact['phone']}")
    if contact.get('location'):
        print(f"📍 LOCATION: {contact['location']}")
    
    if parsed_info.get('years_of_experience'):
        print(f"💼 YEARS OF EXPERIENCE: {parsed_info['years_of_experience']}")
    
    # Skills
    skills = parsed_info.get('skills', [])
    if skills:
        print(f"\n🛠️  SKILLS:")
        for i, skill in enumerate(skills, 1):
            print(f"   {i}. {skill}")
    
    # Summary
    summary = parsed_info.get('summary', '')
    if summary:
        print(f"\n📝 SUMMARY:")
        for line in summary.split('\n'):
            if line.strip():
                print(f"   • {line.strip()}")
    
    # Highlights
    highlights = parsed_info.get('highlights', '')
    if highlights:
        print(f"\n⭐ HIGHLIGHTS:")
        for line in highlights.split('\n'):
            if line.strip():
                print(f"   • {line.strip()}")
    
    # Experience
    experience_entries = parsed_info.get('experience_entries', [])
    if experience_entries:
        print(f"\n💼 WORK EXPERIENCE:")
        for i, exp in enumerate(experience_entries, 1):
            print(f"\n   {i}. {exp['start']} - {exp['end']}")
            if exp['title']:
                print(f"      Position: {exp['title']}")
            if exp['company']:
                print(f"      Company: {exp['company']}")
            if exp['location']:
                print(f"      Location: {exp['location']}")
            if exp['description']:
                print(f"      Description:")
                for desc_line in exp['description'].split('\n'):
                    if desc_line.strip():
                        print(f"        • {desc_line.strip()}")
    
    # Education
    education_entries = parsed_info.get('education_entries', [])
    if education_entries:
        print(f"\n🎓 EDUCATION:")
        for i, edu in enumerate(education_entries, 1):
            print(f"\n   {i}. Year: {edu['year']}")
            if edu['degree']:
                print(f"      Degree: {edu['degree']}")
            if edu['institution']:
                print(f"      Institution: {edu['institution']}")
            if edu['details']:
                print(f"      Details:")
                for detail_line in edu['details'].split('\n'):
                    if detail_line.strip():
                        print(f"        • {detail_line.strip()}")
    
    print("\n" + "=" * 60)


def get_user_input_for_sql_save() -> tuple[bool, str]:
    """
    Get user input for whether to save to SQL and application role.
    Returns (save_to_sql, application_role)
    """
    while True:
        save_choice = input("\n💾 Save extracted data to SQL database? (y/n): ").lower().strip()
        if save_choice in ['y', 'yes', 'n', 'no']:
            break
        print("Please enter 'y' for yes or 'n' for no.")
    
    if save_choice in ['y', 'yes']:
        application_role = input("📝 Enter the application role (optional): ").strip()
        return True, application_role if application_role else None
    
    return False, None


if __name__ == '__main__':
    import sys
    
    # Get PDF path from command line argument or use default
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = '../data/example.pdf'
    
    print(f"📄 Extracting information from: {pdf_path}")
    
    # Extract text and parse information
    raw_text = extract_text_from_pdf(pdf_path)
    if not raw_text:
        print("❌ Failed to extract text from PDF")
        
        # For testing purposes, create dummy data if PDF extraction fails
        use_dummy = input("🧪 Use dummy data for testing SQL save feature? (y/n): ").lower().strip()
        if use_dummy in ['y', 'yes']:
            parsed_info = {
                'name': 'John Doe',
                'contact': {
                    'email': 'john.doe@example.com',
                    'phone': '555-123-4567',
                    'location': 'New York, NY'
                },
                'years_of_experience': 5,
                'skills': ['Python', 'SQL', 'Machine Learning', 'Data Analysis'],
                'experience_entries': [],
                'education_entries': []
            }
            pdf_path = 'dummy_cv.pdf'
        else:
            sys.exit(1)
    else:
        parsed_info = extract_info(raw_text)
    
    # Display extracted information
    print("\n📋 Extracted Information:")
    print("=" * 50)
    
    # Show key information
    if parsed_info.get('name'):
        print(f"👤 Name: {parsed_info['name']}")
    
    contact = parsed_info.get('contact', {})
    if contact.get('email'):
        print(f"📧 Email: {contact['email']}")
    if contact.get('phone'):
        print(f"📞 Phone: {contact['phone']}")
    if contact.get('location'):
        print(f"📍 Location: {contact['location']}")
    
    if parsed_info.get('years_of_experience'):
        print(f"💼 Years of Experience: {parsed_info['years_of_experience']}")
    
    skills = parsed_info.get('skills', [])
    if skills:
        print(f"🛠️  Skills: {', '.join(skills[:5])}{'...' if len(skills) > 5 else ''}")
    
    print("\n" + "=" * 50)
    
    # Ask user if they want to save to SQL
    save_to_sql, application_role = get_user_input_for_sql_save()
    
    if save_to_sql:
        success = save_to_database(parsed_info, pdf_path, application_role)
        if success:
            print("🎉 Data successfully saved to database!")
        else:
            print("⚠️  Failed to save data to database.")
    else:
        print("📊 Data not saved to database.")
      # Optionally display full parsed information
    show_details = input("\n🔍 Show detailed extraction results? (y/n): ").lower().strip()
    if show_details in ['y', 'yes']:
        display_extracted_info_formatted(parsed_info)
    
    # Also offer to show raw extraction data
    show_raw = input("\n🔧 Show raw extraction data? (y/n): ").lower().strip()
    if show_raw in ['y', 'yes']:
        print("\n📋 Raw Extraction Results:")
        print("=" * 50)
        for k, v in parsed_info.items():
            print(f"{k}: {v}\n")