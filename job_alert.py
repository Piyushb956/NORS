from models import *
from recommendation import get_recommendations
from mailer import send_job_email



def send_daily_alerts():

    users = User.query.all()

    for user in users:

        recommendations = get_recommendations(
            user.id
        )

        new_jobs = []

        for job in recommendations:

            
            already_sent = EmailLog.query.filter_by(
                user_id=user.id,
                job_id=job["job"].id
            ).first()

            if not already_sent:

                new_jobs.append(job)

        if new_jobs:

            send_job_email(
                user.email,
                new_jobs[:5]
            )

            for job in new_jobs[:5]:

                alert = EmailLog(
                    user_id=user.id,
                    job_id=job["job"].id
                )

                db.session.add(alert)

    db.session.commit()