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

    return score, matched_skills