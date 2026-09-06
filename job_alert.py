from models import User, EmailLog, db
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

        if not new_jobs:
            continue

        try:

            send_job_email(
                user.email,
                new_jobs[:5]
            )

        except Exception as e:

            print(
                f"Email failed for {user.email}: {e}"
            )

            continue

        for job in new_jobs[:5]:

            db.session.add(
                EmailLog(
                    user_id=user.id,
                    job_id=job["job"].id
                )
            )

    db.session.commit()