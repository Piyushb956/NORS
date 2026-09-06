from datetime import datetime, timedelta

from models import Job, db


def delete_old_jobs(app):

    with app.app_context():

        cutoff = datetime.utcnow() - timedelta(days=1)

        deleted = Job.query.filter(
            Job.created_at < cutoff
        ).delete()

        db.session.commit()

        print(f"Deleted {deleted} jobs")