#!/usr/bin/env python3
"""
Extract all CV data from PDF files and create a comprehensive CSV
Format: ID,Resume_str,Resume_html,Category
"""
import os
import sys
import csv
import re
from pathlib import Path

from .pdf_extractor import PDFExtractor
from .regex_extractor import RegexExtractor

# Define project root for data paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / 'data'

def extract_id_from_filename(filename):
    match = re.search(r'(\d{8})\.pdf$', filename)
    if match:
        return match.group(1)
    return None

def clean_text_for_csv(text):
    if not text:
        return ""
    
    # Replace multiple whitespace with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text

def generate_html_from_text(text, category):
    """Generate basic HTML structure from extracted text"""
    if not text:
        return ""
    
    # Split text into sections based on common CV patterns
    sections = {}
    current_section = "summary"
    current_text = ""
    
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Detect section headers
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in ['summary', 'objective', 'profile']):
            if current_text:
                sections[current_section] = current_text.strip()
            current_section = "summary"
            current_text = ""
        elif any(keyword in line_lower for keyword in ['experience', 'work history', 'employment']):
            if current_text:
                sections[current_section] = current_text.strip()
            current_section = "experience"
            current_text = ""
        elif any(keyword in line_lower for keyword in ['education', 'academic']):
            if current_text:
                sections[current_section] = current_text.strip()
            current_section = "education"
            current_text = ""
        elif any(keyword in line_lower for keyword in ['skills', 'technical skills', 'competencies']):
            if current_text:
                sections[current_section] = current_text.strip()
            current_section = "skills"
            current_text = ""
        else:
            current_text += " " + line
    
    # Add the last section
    if current_text:
        sections[current_section] = current_text.strip()
    
    # Generate HTML structure
    html_parts = ['<div class="fontsize fontface vmargins hmargins linespacing pagesize" id="document">']
    
    # Name section
    html_parts.append('<div class="section firstsection" id="SECTION_NAME" style="padding-top:0px;">')
    html_parts.append('<div class="paragraph PARAGRAPH_NAME firstparagraph" style="padding-top:0px;">')
    html_parts.append(f'<div class="name" itemprop="name"><span class="field">{category.replace("_", " ").title()}</span></div>')
    html_parts.append('</div></div>')
    
    # Summary section
    if "summary" in sections:
        html_parts.append('<div class="section" id="SECTION_SUMM" style="padding-top:0px;">')
        html_parts.append('<div class="heading"><div class="sectiontitle">Summary</div></div>')
        html_parts.append('<div class="paragraph firstparagraph" style="padding-top:0px;">')
        html_parts.append(f'<div class="field singlecolumn">{sections["summary"]}</div>')
        html_parts.append('</div></div>')
    
    # Experience section
    if "experience" in sections:
        html_parts.append('<div class="section" id="SECTION_EXPR" style="padding-top:0px;">')
        html_parts.append('<div class="heading"><div class="sectiontitle">Experience</div></div>')
        html_parts.append('<div class="paragraph firstparagraph" style="padding-top:0px;">')
        html_parts.append(f'<div class="field singlecolumn">{sections["experience"]}</div>')
        html_parts.append('</div></div>')
    
    # Education section
    if "education" in sections:
        html_parts.append('<div class="section" id="SECTION_EDUC" style="padding-top:0px;">')
        html_parts.append('<div class="heading"><div class="sectiontitle">Education</div></div>')
        html_parts.append('<div class="paragraph firstparagraph" style="padding-top:0px;">')
        html_parts.append(f'<div class="field singlecolumn">{sections["education"]}</div>')
        html_parts.append('</div></div>')
    
    # Skills section
    if "skills" in sections:
        html_parts.append('<div class="section" id="SECTION_SKLL" style="padding-top:0px;">')
        html_parts.append('<div class="heading"><div class="sectiontitle">Skills</div></div>')
        html_parts.append('<div class="paragraph firstparagraph" style="padding-top:0px;">')
        html_parts.append(f'<div class="field singlecolumn">{sections["skills"]}</div>')
        html_parts.append('</div></div>')
    
    html_parts.append('</div>')
    
    return ''.join(html_parts)

def process_cv_directory():
    """Process all CV files and generate CSV data"""
    cv_base_path = str(DATA_DIR / 'cv')
    pdf_extractor = PDFExtractor()
    regex_extractor = RegexExtractor()
    
    cv_data = []
    processed_count = 0
    error_count = 0
    
    print("Starting CV extraction process...")
    
    # Iterate through all category directories
    for category in os.listdir(cv_base_path):
        category_path = os.path.join(cv_base_path, category)
        
        if not os.path.isdir(category_path):
            continue
            
        print(f"Processing category: {category}")
        
        # Process all PDF files in the category
        pdf_files = [f for f in os.listdir(category_path) if f.endswith('.pdf')]
        
        for pdf_file in pdf_files:
            try:
                # Extract ID from filename
                cv_id = extract_id_from_filename(pdf_file)
                if not cv_id:
                    print(f"Warning: Could not extract ID from {pdf_file}")
                    continue
                
                pdf_path = os.path.join(category_path, pdf_file)
                
                # Extract text from PDF
                raw_text = pdf_extractor.extract_text(pdf_path)
                
                if not raw_text or len(raw_text.strip()) < 50:
                    print(f"Warning: Little or no text extracted from {pdf_file}")
                    error_count += 1
                    continue
                
                # Parse structured information
                parsed_info = regex_extractor.extract_cv_info(raw_text)
                
                # Clean and format the text
                resume_str = clean_text_for_csv(raw_text)
                
                # Generate HTML version
                resume_html = generate_html_from_text(raw_text, category)
                
                # Create CSV record
                cv_record = {
                    'ID': cv_id,
                    'Resume_str': resume_str,
                    'Resume_html': resume_html,
                    'Category': category
                }
                
                cv_data.append(cv_record)
                processed_count += 1
                
                if processed_count % 50 == 0:
                    print(f"Processed {processed_count} CVs...")
                
            except Exception as e:
                print(f"Error processing {pdf_file}: {str(e)}")
                error_count += 1
                continue
    
    print(f"Extraction complete! Processed: {processed_count}, Errors: {error_count}")
    return cv_data

def save_to_csv(cv_data, output_file="data/extracted_cvs.csv"):
    """Save CV data to CSV file"""
    out_path = Path(output_file)
    if not out_path.is_absolute():
        out_path = BASE_DIR / output_file
    print(f"Saving {len(cv_data)} records to {out_path}...")
    
    # Ensure output directory exists
    os.makedirs(out_path.parent, exist_ok=True)
    
    with open(out_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['ID', 'Resume_str', 'Resume_html', 'Category']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for record in cv_data:
            writer.writerow(record)
    
    print(f"CSV file saved successfully: {output_file}")

def create_lookup_csv(cv_data, output_file="data/cv_lookup.csv"):
    """Create a simplified lookup CSV for quick search"""
    out_path = Path(output_file)
    if not out_path.is_absolute():
        out_path = BASE_DIR / output_file
    print(f"Creating lookup CSV with {len(cv_data)} records at {out_path}...")
    
    lookup_data = []
    for record in cv_data:
        # Extract key information for quick lookup
        text = record['Resume_str']
        
        # Extract skills, education, experience keywords
        text_lower = text.lower()
        
        # Simple keyword extraction
        skills_keywords = []
        for skill in ['python', 'java', 'javascript', 'react', 'html', 'css', 'sql', 'mongodb', 
                     'aws', 'docker', 'kubernetes', 'git', 'machine learning', 'data science']:
            if skill in text_lower:
                skills_keywords.append(skill)
        
        lookup_record = {
            'ID': record['ID'],
            'Category': record['Category'],
            'Text_Length': len(text),
            'Keywords': ', '.join(skills_keywords),
            'Text_Preview': text[:200] + '...' if len(text) > 200 else text
        }
        
        lookup_data.append(lookup_record)
    
    with open(out_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['ID', 'Category', 'Text_Length', 'Keywords', 'Text_Preview']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for record in lookup_data:
            writer.writerow(record)
    
    print(f"Lookup CSV saved: {output_file}")

def main():
    """Main extraction process"""
    print("CV to CSV Extraction Tool")
    print("=" * 40)
    
    # Check if CV directory exists
    cv_dir = DATA_DIR / 'cv'
    if not cv_dir.exists():
        print(f"Error: CV directory '{cv_dir}' not found!")
        return
    
    # Process all CVs
    cv_data = process_cv_directory()
    
    if not cv_data:
        print("No CV data extracted!")
        return
    
    # Save main CSV
    save_to_csv(cv_data, str(DATA_DIR / 'extracted_cvs.csv'))
    
    # Save lookup CSV
    create_lookup_csv(cv_data, str(DATA_DIR / 'cv_lookup.csv'))
    
    # Display summary
    print(f"\nExtraction Summary:")
    print(f"Total CVs processed: {len(cv_data)}")
    
    categories = {}
    for record in cv_data:
        category = record['Category']
        categories[category] = categories.get(category, 0) + 1
    
    print(f"Categories found:")
    for category, count in sorted(categories.items()):
        print(f"  {category}: {count} CVs")
    
    print(f"\nFiles generated:")
    print(f"  data/extracted_cvs.csv - Full CV data")
    print(f"  data/cv_lookup.csv - Quick lookup data")

if __name__ == "__main__":
    main()
