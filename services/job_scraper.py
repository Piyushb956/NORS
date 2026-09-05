import requests
import json

from services.embedding_service import generate_embedding
from models import Job
from app import db
from bs4 import BeautifulSoup


def scrape_remotive():

    url = "https://remoteok.com/api"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Failed:", response.status_code)
        return []

    data = response.json()
    jobs = []

    for item in data[1:]:
        jobs.append({
            "company": item.get("company", ""),
            "title": item.get("position", ""),
            "location": item.get("location", "Remote"),
            "skills": ",".join(item.get("tags", [])),
            "apply_url": item.get("url", "")
        })

    return jobs


def save_jobs(jobs):

    added = 0

    for i, item in enumerate(jobs):

        existing = Job.query.filter_by(
            apply_url=item["apply_url"]
        ).first()

        if existing:
            continue

        job_text = f"""
        {item['title']}
        {item['company']}
        {item['skills']}
        """
        embedding = generate_embedding(job_text)
        embedding_json = json.dumps(embedding.tolist())

        new_job = Job(
            company=item["company"],
            title=item["title"],
            location=item["location"],
            skills=item["skills"],
            apply_url=item["apply_url"],
            embedding=embedding_json
        )

        db.session.add(new_job)
        added += 1

        # commit every 20 jobs instead of holding everything until the end
        if added % 20 == 0:
            db.session.commit()

    db.session.commit()  # final commit for any remainder
    print(f"{added} jobs added")


def scrape_jobs():

    all_jobs = []
    all_jobs.extend(scrape_remotive())

    save_jobs(all_jobs)