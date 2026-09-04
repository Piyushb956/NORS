import json
from sklearn.metrics.pairwise import cosine_similarity

def calculate_embedding_match(user_embedding, job_embedding):

    user_vector = json.loads(user_embedding)

    job_vector = json.loads(job_embedding)

    return cosine_similarity(
        [user_vector],
        [job_vector]
    )[0][0]
    
    
    
def calculate_match(user_skills, job_skills):

    if not user_skills or not job_skills:
        return 0, []

    user_set = {
        skill.strip().lower()
        for skill in user_skills.split(",")
    }

    job_set = {
        skill.strip().lower()
        for skill in job_skills.split(",")
    }

    matched_skills = list(
        user_set.intersection(job_set)
    )

    score = round(
        len(matched_skills)
        /
        len(user_set.union(job_set))
        * 100
    )

    return score , matched_skills

def calculate_final_score(skill_score,embedding_score):

    return (
        skill_score * 0.6
        +
        embedding_score * 40
    )*0.2