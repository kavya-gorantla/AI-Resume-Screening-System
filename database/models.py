import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from config import DB_URI

Base = declarative_base()

class Candidate(Base):
    __tablename__ = 'candidates'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    education = Column(Text, nullable=True)
    experience = Column(Text, nullable=True)
    skills = Column(Text, nullable=True)
    # We will store embeddings separately in FAISS, but could store a serialized JSON or string if needed
    # For now, FAISS holds the vectors, and the FAISS index matches the SQLite Candidate ID
    
    # We can store similarity score per specific job, but since it's dynamic based on the selected JD,
    # it's usually better to compute it on the fly or store it in a result table if persistence is needed.
    # For this dashboard, we can compute it on the fly or hold it in session state.

class Job(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=False)
    # Similarly, FAISS can hold job embeddings if there are many, or we just encode the current one.

engine = create_engine(DB_URI, echo=False)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
