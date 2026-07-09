import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Directories
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_DIR = os.path.join(BASE_DIR, "database")
RESUMES_DIR = os.path.join(BASE_DIR, "resumes")
JD_DIR = os.path.join(BASE_DIR, "job_descriptions")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

# Ensure directories exist
for directory in [DATA_DIR, DB_DIR, RESUMES_DIR, JD_DIR, OUTPUT_DIR]:
    os.makedirs(directory, exist_ok=True)

# Database
DB_PATH = os.path.join(DB_DIR, "resumes.db")
DB_URI = f"sqlite:///{DB_PATH}"

# Model configurations
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# NLP configurations
SPACY_MODEL = "en_core_web_sm"
