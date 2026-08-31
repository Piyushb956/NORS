from flask_mail import Message
from app import mail

def send_job_email(user, jobs):

    body = f"""
Hello {user.username},

Here are jobs matching your profile:

"""

    for job in jobs:

        body += f"""
{job.title}
{job.company}
{job.location}

Apply:
{job.apply_url}

"""

    msg = Message(
        subject="Nors Job Recommendations",
        recipients=[user.email],
        body=body
    )

    mail.send(msg)