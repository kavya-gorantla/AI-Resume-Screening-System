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
    if not nlp:
        return "Unknown"
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
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
