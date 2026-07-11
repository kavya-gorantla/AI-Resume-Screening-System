import re
import spacy
import pandas as pd
from config import DATA_DIR
import os

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    nlp = None

def extract_email(text):
    email = re.findall(r'[\w\.-]+@[\w\.-]+', text)
    return email[0] if email else None

def extract_phone(text):
    phone = re.findall(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', text)
    return phone[0] if phone else None

def extract_name(text):
    """
    Multi-strategy name extraction:
    1. Top-of-resume heuristic — names almost always appear in the first few lines
    2. spaCy NER — finds PERSON entities in full text
    3. Regex fallback — looks for 2–3 consecutive capitalized words
    """
    if not text:
        return "Unknown"

    # ── Strategy 1: Top-of-resume lines ───────────────────────────────────────
    # Candidate name is almost always in the first 5 non-empty lines
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    name_pattern = re.compile(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}$')
    # Skip lines that look like headers (all-caps labels), emails, phones, URLs
    skip_pattern = re.compile(
        r'@|http|linkedin|github|www\.|^\+?\d|resume|curriculum|vitae|cv\b',
        re.IGNORECASE
    )
    for line in lines[:8]:
        # Remove common titles/suffixes that might be inline
        clean_line = re.sub(
            r'\b(Mr\.?|Mrs\.?|Ms\.?|Dr\.?|Prof\.?|Jr\.?|Sr\.?|II|III|IV)\b',
            '', line, flags=re.IGNORECASE
        ).strip()
        if skip_pattern.search(clean_line):
            continue
        if name_pattern.match(clean_line):
            return clean_line.strip()

    # ── Strategy 2: spaCy NER on full text ────────────────────────────────────
    if nlp:
        try:
            # Only analyze first 1000 chars for speed
            doc = nlp(text[:1000])
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    name = ent.text.strip()
                    # Filter out very short or very long matches
                    if 4 <= len(name) <= 40 and len(name.split()) >= 2:
                        return name
        except Exception:
            pass

    # ── Strategy 3: Regex fallback ────────────────────────────────────────────
    # Find first occurrence of 2-3 consecutive Title Case words
    regex_match = re.search(r'\b([A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\b', text[:500])
    if regex_match:
        return regex_match.group(1)

    return "Unknown"

def load_skills_db():
    skills_path = os.path.join(DATA_DIR, 'skills.csv')
    if os.path.exists(skills_path):
        df = pd.read_csv(skills_path)
        return set(df['skill'].str.lower().tolist())
    else:
        # Fallback basic skills
        return {"python", "sql", "java", "c++", "machine learning", "nlp", "aws", "docker", "tensorflow", "pytorch", "react", "node.js"}

def extract_skills(text):
    skills_db = load_skills_db()
    text_lower = text.lower()
    extracted_skills = set()
    
    # Tokenize and check for single/multi-word skills
    for skill in skills_db:
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            extracted_skills.add(skill.title())
            
    return list(extracted_skills)

def load_education_db():
    edu_path = os.path.join(DATA_DIR, 'education.csv')
    if os.path.exists(edu_path):
        df = pd.read_csv(edu_path)
        return set(df['degree'].str.lower().tolist())
    else:
        return {"b.tech", "b.e.", "mca", "m.tech", "b.sc", "m.sc", "mba", "phd", "bachelor", "master"}

def extract_education(text):
    edu_db = load_education_db()
    text_lower = text.lower()
    extracted_edu = set()
    
    for edu in edu_db:
        if re.search(r'\b' + re.escape(edu) + r'\b', text_lower):
            extracted_edu.add(edu.upper())
            
    return list(extracted_edu)

def extract_experience_text(text):
    # This is a very rough heuristic for experience section extraction
    # In a real-world scenario, you would use a more robust trained NER model or LLM
    text_lower = text.lower()
    if "experience" in text_lower:
        idx = text_lower.find("experience")
        return text[idx:idx+1000] # Return roughly the section after "experience"
    return "Not clearly found."
