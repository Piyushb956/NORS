import requests

from models import Job
from app import db


def get_jobs():

    url = "https://remoteok.com/api"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        url,
        headers=headers
    )

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

    for item in jobs:

        existing = Job.query.filter_by(
            apply_url=item["apply_url"]
        ).first()

        if existing:
            continue

        new_job = Job(
            company=item["company"],
            title=item["title"],
            location=item["location"],
            skills=item["skills"],
            apply_url=item["apply_url"]
        )

        db.session.add(new_job)

        added += 1

    db.session.commit()

    print(f"{added} jobs added")


def scrape_jobs():

    jobs = get_jobs()

    save_jobs(jobs)