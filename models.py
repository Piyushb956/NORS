from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime


   

db = SQLAlchemy()

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100),unique= True,nullable=False)
    email = db.Column(db.String(120),unique=True,nullable=False)
    password = db.Column(db.String(255),unique=True,nullable=False)



class CareerProfile(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    target_role = db.Column(db.Text)

    skills = db.Column(db.Text)

    location = db.Column(db.Text)

    # experience = db.Column(db.String(50))

    # work_mode = db.Column(db.String(50))

    # job_type = db.Column(db.String(50))

    alerts_enabled = db.Column(
        db.Boolean,
        default=True
    )
    
    
class Job(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    company = db.Column(db.String(100))

    title = db.Column(db.String(100))

    location = db.Column(db.String(100))

    skills = db.Column(db.Text)

    apply_url = db.Column(db.Text)
    
    
    
    
class Application(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    job_id = db.Column(
        db.Integer,
        db.ForeignKey("job.id")
    )

    status = db.Column(
        db.String(50),
        default="Applied"
    )

    applied_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
    
class EmailLog(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    job_id = db.Column(
        db.Integer,
        db.ForeignKey("job.id")
    )

    sent_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )