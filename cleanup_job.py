from datetime import datetime,timedelta


from models import Job,db

def delete_old_jobs(app):

    with app.app_context():

        cutoff = datetime.utcnow() - timedelta(days=4)

        old_jobs = Job.query.filter(
            Job.created_at < cutoff
        ).all()

        for job in old_jobs:
            db.session.delete(job)

        db.session.commit()

        print(
            f"Deleted {len(old_jobs)} jobs"
        )
        
