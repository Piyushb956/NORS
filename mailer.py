from flask_mail import Mail, Message

mail = Mail()


def send_job_email(user_email, recommendations):

   

    body = f"""
    
        Hi,

        We found {len(recommendations)} new jobs matching your profile.

        """

    for item in recommendations:

        job = item["job"]

        body += f"""
        

         ------------------------------------------

            Title: {job.title}

            Company: {job.company}

            Location: {job.location}

            Skills: {job.skills}

            Apply Here: {job.apply_url}

            Match Score: {item['score']:.2f}%

         ----------------------------------------
        """

    body += """

        Best Regards,
        Nors Team
        """

    msg = Message(
        subject="New Job Recommendations From Nors",
        recipients=[user_email],
        body=body
    )

    mail.send(msg)