# AI Resume Screening & Candidate Ranking System

An end-to-end AI recruitment assistant that automates the initial resume screening process.

## Features

- **Resume Upload**: Upload multiple PDF and DOCX files.
- **Parsing**: Extracts text automatically from supported formats.
- **NLP Extraction**: Uses `spaCy` and regular expressions to extract Name, Email, Phone, Skills, and Education.
- **Embeddings**: Uses `sentence-transformers/all-MiniLM-L6-v2` to convert text into semantic vectors.
- **Vector Search**: Uses FAISS for incredibly fast similarity search.
- **Candidate Ranking**: Weighted scoring system factoring in semantic similarity and skill gap analysis.
- **Dashboard**: Professional Streamlit UI with Plotly charts.
- **Export**: Download ranked candidates as CSV.

## Folder Structure

- `app.py`: Main Streamlit app.
- `config.py`: Project configuration and paths.
- `database/`: SQLite database setup and ORM models.
- `parser/`: Handlers for PDF and DOCX files.
- `preprocessing/`: Text cleaning utilities.
- `extraction/`: Entity extraction logic (Skills, Education, etc.).
- `embeddings/`: Sentence transformer models.
- `ranking/`: FAISS index and scoring logic.
- `utils/`: Mocked LLM logic for summaries (as no API key is present).

## Setup & Installation

1. Create a virtual environment (optional but recommended).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Download the spaCy model:
   ```bash
   python -m spacy download en_core_web_sm
   ```
4. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

## Usage

1. Go to **Upload Resumes** to upload `.pdf` or `.docx` candidate resumes.
2. Go to **Job Description** to paste a JD and click "Analyze & Rank Candidates".
3. View the results on the **Dashboard** or inspect individual profiles in **Candidates**.
