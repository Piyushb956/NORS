from models import Job, CareerProfile
from services.job_matcher import calculate_match


def get_recommendations(user_id):

    profile = CareerProfile.query.filter_by(
        user_id=user_id
    ).first()

    if not profile:
        return []

    recommendations = []

    jobs = Job.query.all()

    for job in jobs:

        score, matched_skills = calculate_match(
            profile.skills,
            job.skills
        )

        if score > 0:

            recommendations.append({
                "job": job,
                "score": score,
                "matched_skills": matched_skills
            })

    recommendations.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return recommendations