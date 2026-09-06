import requests

from models import Job, db


def scrape_remoteok():

    url = "https://remoteok.com/api"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

    except Exception as e:

        print(f"[RemoteOK] Scraping failed: {e}")

        return []

    jobs = []

    for item in data[1:]:

        apply_url = item.get("url")

        if not apply_url:
            continue

        jobs.append(
            {
                "company": item.get("company", ""),
                "title": item.get("position", ""),
                "location": item.get("location", "Remote"),
                "skills": ",".join(item.get("tags", [])),
                "apply_url": apply_url
            }
        )

    print(f"[RemoteOK] Fetched {len(jobs)} jobs")

    return jobs


def save_jobs(jobs):

    if not jobs:
        print("No jobs to save")
        return

    existing_urls = {
        job.apply_url
        for job in db.session.query(Job.apply_url).all()
    }

    added = 0

    for item in jobs:

        if item["apply_url"] in existing_urls:
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

        if added % 20 == 0:
            db.session.commit()

    db.session.commit()

    print(f"{added} new jobs added")


def scrape_jobs():

    all_jobs = []

    all_jobs.extend(
        scrape_remoteok()
    )

    save_jobs(all_jobs)