import streamlit as st
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy.orm import Session
from database.models import engine, Candidate, Job, init_db
from parser.pdf_parser import extract_text_from_pdf
from parser.docx_parser import extract_text_from_docx
from preprocessing.clean_text import clean_text
from extraction.extractor import extract_name, extract_email, extract_phone, extract_skills, extract_education, extract_experience_text
from embeddings.embedding_model import get_embedding
from ranking.faiss_search import FaissIndex
from ranking.similarity import calculate_skill_match, calculate_education_match, calculate_final_score
from utils.llm_mock import generate_candidate_summary, analyze_skill_gap, generate_resume_tips
from config import RESUMES_DIR, JD_DIR

st.set_page_config(page_title="AI Resume Screener", layout="wide", page_icon="📄")

# Custom CSS for a professional look
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #4CAF50;
    }
    .candidate-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .tip-box {
        background-color: #eef2ff;
        border-left: 4px solid #4f46e5;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 10px;
        color: #1e1e2f;
    }
    h1, h2, h3 {
        color: #2c3e50;
        font-family: 'Inter', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# Initialize DB on first run
@st.cache_resource
def setup_db():
    init_db()

setup_db()

# Session State
if 'faiss_index' not in st.session_state:
    st.session_state.faiss_index = FaissIndex()
if 'ranked_candidates' not in st.session_state:
    st.session_state.ranked_candidates = []

st.sidebar.title("📄 AI Resume Screener")
st.sidebar.markdown("---")
menu = st.sidebar.radio("Navigation", ["Dashboard", "Upload Resumes", "Job Description", "Candidates"])
st.sidebar.markdown("---")
st.sidebar.info("Upload resumes and a Job Description to let the AI rank and provide feedback on candidates.")

def save_uploaded_file(uploaded_file, dest_dir):
    file_path = os.path.join(dest_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

if menu == "Upload Resumes":
    st.header("📤 Upload Resumes")
    st.markdown("Upload multiple candidate resumes in **PDF** or **DOCX** format.")
    
    uploaded_files = st.file_uploader("", type=['pdf', 'docx'], accept_multiple_files=True)
    
    if st.button("Process Resumes", type="primary"):
        if uploaded_files:
            with st.spinner("Extracting and vectorizing resumes..."):
                with Session(engine) as session:
                    new_vectors = []
                    new_ids = []
                    for uploaded_file in uploaded_files:
                        file_path = save_uploaded_file(uploaded_file, RESUMES_DIR)
                        
                        # Parsing
                        if file_path.endswith('.pdf'):
                            raw_text = extract_text_from_pdf(file_path)
                        else:
                            raw_text = extract_text_from_docx(file_path)
                            
                        # Preprocessing & Extraction
                        cleaned = clean_text(raw_text)
                        name = extract_name(raw_text)
                        email = extract_email(raw_text)
                        phone = extract_phone(raw_text)
                        skills = extract_skills(raw_text)
                        education = extract_education(raw_text)
                        experience = extract_experience_text(raw_text)
                        
                        # Save to DB
                        cand = Candidate(
                            name=name, email=email, phone=phone,
                            education="; ".join(education),
                            experience=experience,
                            skills="; ".join(skills)
                        )
                        session.add(cand)
                        session.commit()
                        
                        # Embedding
                        vector = get_embedding(cleaned)
                        new_vectors.append(vector)
                        new_ids.append(cand.id)
                        
                    # Add to FAISS
                    if new_vectors:
                        st.session_state.faiss_index.add_vectors(new_vectors, new_ids)
                        
            st.success(f"✅ Successfully processed {len(uploaded_files)} resumes! Now go to the Job Description tab.")
        else:
            st.warning("Please upload at least one resume.")

elif menu == "Job Description":
    st.header("📝 Job Description Details")
    st.markdown("Paste the target job description to match candidates against.")
    jd_text = st.text_area("", height=250, placeholder="Paste JD here (e.g., Responsibilities, Qualifications, Skills)...")
    
    if st.button("Analyze & Rank Candidates", type="primary"):
        if jd_text:
            with st.spinner("Analyzing semantics and calculating skill gaps..."):
                cleaned_jd = clean_text(jd_text)
                jd_skills = extract_skills(jd_text)
                jd_edu = extract_education(jd_text)
                jd_vector = get_embedding(cleaned_jd)
                
                # Perform Search
                results = st.session_state.faiss_index.search(jd_vector, k=50) # top 50
                
                ranked_candidates = []
                with Session(engine) as session:
                    for db_id, sim_score in results:
                        cand = session.get(Candidate, db_id)
                        if cand:
                            cand_skills = cand.skills.split("; ") if cand.skills else []
                            cand_edu = cand.education.split("; ") if cand.education else []
                            
                            skill_score = calculate_skill_match(cand_skills, jd_skills)
                            edu_score = calculate_education_match(cand_edu, jd_edu)
                            
                            # Calculate final score
                            final_score = calculate_final_score(sim_score, skill_score, edu_score, exp_score=1.0)
                            
                            # LLM Analysis Mock
                            summary = generate_candidate_summary({'name': cand.name, 'skills': cand_skills})
                            gap = analyze_skill_gap(cand_skills, jd_skills)
                            tips = generate_resume_tips(cand_skills, jd_skills, final_score)
                            
                            ranked_candidates.append({
                                'id': cand.id,
                                'Name': cand.name,
                                'Email': cand.email,
                                'Final Score': round(final_score, 2),
                                'Semantic Score': round(sim_score, 4),
                                'Skills Matched': gap['matched'],
                                'Skills Missing': gap['missing'],
                                'Summary': summary,
                                'Tips': tips
                            })
                
                # Sort descending by Final Score
                ranked_candidates.sort(key=lambda x: x['Final Score'], reverse=True)
                st.session_state.ranked_candidates = ranked_candidates
                
            st.success("✅ Ranking complete! Go to the Dashboard to view results.")
        else:
            st.warning("Please provide a Job Description.")

elif menu == "Dashboard":
    st.header("📊 Executive Dashboard")
    
    if not st.session_state.ranked_candidates:
        st.info("No candidates ranked yet. Please upload resumes and process a Job Description.")
    else:
        df = pd.DataFrame(st.session_state.ranked_candidates)
        
        # Top Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("👥 Total Screened", len(df))
        with col2:
            st.metric("🏆 Top Candidate", df.iloc[0]['Name'])
        with col3:
            st.metric("⭐ Top Score", f"{df.iloc[0]['Final Score']}%")
            
        st.markdown("<br>", unsafe_allow_html=True)
            
        # Charts
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("Score Distribution")
            fig = px.histogram(df, x='Final Score', nbins=10, color_discrete_sequence=['#4f46e5'])
            fig.update_layout(margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
            
        with col_chart2:
            st.subheader("Top 5 Candidates")
            top5 = df.head(5)
            fig2 = px.bar(top5, x='Name', y='Final Score', color='Final Score', color_continuous_scale='Blues')
            fig2.update_layout(margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig2, use_container_width=True)
        
        # Data Table
        st.subheader("📋 Ranked Candidates Board")
        
        # Use data editor for a cleaner look
        display_df = df[['Name', 'Email', 'Final Score', 'Semantic Score']].copy()
        display_df.index = display_df.index + 1
        st.dataframe(display_df.style.highlight_max(subset=['Final Score'], color='#d4edda'), use_container_width=True)
        
        # Export
        st.markdown("<br>", unsafe_allow_html=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export Results to CSV", csv, "candidates_ranked.csv", "text/csv")

elif menu == "Candidates":
    st.header("👤 Candidate Profiles & AI Feedback")
    if not st.session_state.ranked_candidates:
        st.info("No candidates available.")
    else:
        df = pd.DataFrame(st.session_state.ranked_candidates)
        selected_cand_name = st.selectbox("Select Candidate to Review", df['Name'].tolist())
        
        cand_data = df[df['Name'] == selected_cand_name].iloc[0]
        
        st.markdown("<div class='candidate-card'>", unsafe_allow_html=True)
        
        col_prof1, col_prof2 = st.columns([2, 1])
        with col_prof1:
            st.subheader(f"{cand_data['Name']}")
            st.write(f"📧 **Email:** {cand_data['Email']}")
            st.write(f"🤖 **AI Summary:** {cand_data['Summary']}")
        with col_prof2:
            st.metric("Match Score", f"{cand_data['Final Score']}%")
            
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Skills Analysis
        st.write("### 🛠️ Skills Analysis")
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"✅ Matched Skills ({len(cand_data['Skills Matched'])})")
            for s in cand_data['Skills Matched']:
                st.write(f"- {s}")
        with col2:
            st.error(f"❌ Missing Skills ({len(cand_data['Skills Missing'])})")
            for s in cand_data['Skills Missing']:
                st.write(f"- {s}")
                
        st.markdown("<br>", unsafe_allow_html=True)
        
        # AI Feedback & Improvement Tips (Dynamic Feature)
        st.write("### 💡 AI Resume Feedback & Improvement Tips")
        st.markdown("Actionable suggestions generated dynamically based on the specific job description match.")
        
        if not cand_data.get('Tips'):
            st.info("No specific tips generated for this candidate.")
        else:
            for tip in cand_data['Tips']:
                st.markdown(f"<div class='tip-box'>{tip}</div>", unsafe_allow_html=True)
