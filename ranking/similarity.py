def calculate_skill_match(candidate_skills, required_skills):
    if not required_skills:
        return 0.0
    
    cand_set = set([s.lower() for s in candidate_skills])
    req_set = set([s.lower() for s in required_skills])
    
    match_count = len(cand_set.intersection(req_set))
    return match_count / len(req_set)

def calculate_education_match(candidate_edu, required_edu):
    if not required_edu:
        return 1.0 # If no specific education required, give full points
        
    cand_set = set([e.lower() for e in candidate_edu])
    req_set = set([e.lower() for e in required_edu])
    
    if cand_set.intersection(req_set):
        return 1.0
    return 0.0

def calculate_final_score(semantic_score, skill_score, edu_score, exp_score=1.0):
    """
    Final Score = 60% Semantic Similarity + 20% Skill Match + 10% Experience + 10% Education
    Note: semantic_score from FAISS Inner Product is usually between -1 and 1. We assume it's scaled to [0,1].
    If it's cosine similarity, it's [-1, 1], so we map it to [0,1].
    """
    # Map semantic score to 0-1
    sem_mapped = (semantic_score + 1) / 2 if semantic_score < 0 else semantic_score
    sem_mapped = max(0, min(1, sem_mapped))
    
    final = (0.60 * sem_mapped) + (0.20 * skill_score) + (0.10 * exp_score) + (0.10 * edu_score)
    return final * 100 # percentage
