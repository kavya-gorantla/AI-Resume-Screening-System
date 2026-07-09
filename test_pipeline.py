import os
from database.models import init_db, SessionLocal, Candidate
from parser.pdf_parser import extract_text_from_pdf
from preprocessing.clean_text import clean_text
from extraction.extractor import extract_name, extract_email, extract_phone, extract_skills, extract_education, extract_experience_text
from embeddings.embedding_model import get_embedding
from ranking.faiss_search import FaissIndex

def main():
    # Initialize DB
    init_db()
    
    # Create a dummy text mimicking a resume
    dummy_resume = """
    John Doe
    Email: john.doe@example.com
    Phone: 123-456-7890
    
    Education:
    B.Tech in Computer Science, 2020-2024
    
    Skills: Python, SQL, Machine Learning, AWS, Docker
    
    Experience:
    Software Engineer Intern at Google (6 months)
    Worked on machine learning workflows and database optimization using SQL.
    """
    
    # Preprocess
    cleaned = clean_text(dummy_resume)
    name = extract_name(dummy_resume)
    email = extract_email(dummy_resume)
    phone = extract_phone(dummy_resume)
    skills = extract_skills(dummy_resume)
    education = extract_education(dummy_resume)
    experience = extract_experience_text(dummy_resume)
    
    print("--- Extracted Info ---")
    print(f"Name: {name}")
    print(f"Email: {email}")
    print(f"Phone: {phone}")
    print(f"Skills: {skills}")
    print(f"Education: {education}")
    print(f"Experience: {experience}")
    
    # Database save
    session = SessionLocal()
    cand = Candidate(
        name=name, email=email, phone=phone,
        education="; ".join(education),
        experience=experience,
        skills="; ".join(skills)
    )
    session.add(cand)
    session.commit()
    print(f"Saved Candidate ID: {cand.id}")
    
    # Embedding
    vector = get_embedding(cleaned)
    print(f"Embedding vector dimension: {len(vector)}")
    
    # FAISS
    index = FaissIndex()
    index.add_vectors([vector], [cand.id])
    print(f"FAISS index count: {index.current_count}")
    
    # Search
    query = "Python SQL Machine Learning Developer"
    q_cleaned = clean_text(query)
    q_vector = get_embedding(q_cleaned)
    results = index.search(q_vector, k=5)
    print("--- Search Results ---")
    print(results)

if __name__ == "__main__":
    main()
