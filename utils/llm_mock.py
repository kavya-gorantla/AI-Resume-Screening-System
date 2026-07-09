def generate_candidate_summary(candidate_data):
    """
    Mock LLM: Generates a short summary for the candidate.
    """
    name = candidate_data.get('name', 'Candidate')
    skills = candidate_data.get('skills', [])
    skill_str = ", ".join(skills[:5]) if skills else "various technologies"
    
    return f"{name} is a professional with experience in {skill_str}."

def analyze_skill_gap(candidate_skills, required_skills):
    """
    Mock LLM: Analyzes skill gap.
    """
    cand_set = set([s.lower() for s in candidate_skills])
    req_set = set([s.lower() for s in required_skills])
    
    matched = list(cand_set.intersection(req_set))
    missing = list(req_set.difference(cand_set))
    additional = list(cand_set.difference(req_set))
    
    return {
        "matched": [s.title() for s in matched],
        "missing": [s.title() for s in missing],
        "additional": [s.title() for s in additional]
    }

def generate_strengths_weaknesses(candidate_skills, required_skills):
    """
    Mock LLM: Generates strengths and weaknesses based on skills.
    """
    gap = analyze_skill_gap(candidate_skills, required_skills)
    
    strengths = f"Strong match in {len(gap['matched'])} required skills. Brings additional value with {len(gap['additional'])} extra skills."
    weaknesses = f"Lacks {len(gap['missing'])} required skills, including: {', '.join(gap['missing'][:3])}." if gap['missing'] else "Meets all required skills."
    
    return {
        "strengths": strengths,
        "weaknesses": weaknesses
    }

def generate_resume_tips(candidate_skills, required_skills, final_score):
    """
    Mock LLM: Generates dynamic, actionable tips for the candidate based on their skill gap and score.
    """
    gap = analyze_skill_gap(candidate_skills, required_skills)
    tips = []
    
    # Analyze missing skills
    if gap['missing']:
        critical_missing = gap['missing'][:3]
        tips.append(f"**Skill Acquisition:** Consider gaining practical experience or certifications in: {', '.join(critical_missing)}.")
        tips.append(f"**Resume Update:** If you already have experience with {critical_missing[0]}, make sure it is explicitly stated in your recent projects or experience section.")
    
    # Analyze matched skills
    if gap['matched']:
        top_match = gap['matched'][0]
        tips.append(f"**Highlight Strengths:** Your experience in {top_match} is a strong asset for this role. Emphasize quantifiable achievements related to this skill in your summary.")
        
    # Analyze extra skills
    if gap['additional']:
        tips.append(f"**Differentiate Yourself:** You have bonus skills like {gap['additional'][0]} that aren't strictly required but could set you apart. Mention how these skills bring unique value to the role.")
        
    # General scoring tip
    if final_score < 60:
        tips.append("**Formatting Tip:** Your semantic match score was a bit low. Try tailoring your resume summary and bullet points to more closely mirror the exact language used in the Job Description.")
    elif final_score >= 80:
        tips.append("**Excellent Fit:** You are a highly relevant candidate! Prepare to discuss your specific implementations of the matched skills during the technical interview.")
        
    return tips
