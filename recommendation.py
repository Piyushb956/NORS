import json
from models import *
from services.job_matcher import *



def get_recommendations(user_id):

    profile = CareerProfile.query.filter_by(
        user_id=user_id
    ).first()

    if not profile:
        return []
    
    # resume = Resume.query.filter_by(
    #     user_id=user_id
    # ).first()

    # if not resume:
    #     return []
    
    

    recommendations = []

    jobs = Job.query.all()

    for job in jobs:

        skill_score, matched_skills = calculate_match(profile.skills, job.skills)
        

        
        if skill_score > 0:

            recommendations.append({
                "job": job,
                "score": skill_score,
                
            })
        

    recommendations.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return recommendations