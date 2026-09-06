from flask import Flask , render_template,request,redirect,flash,url_for
from flask_login import LoginManager, login_user,current_user,login_required,logout_user
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from datetime import datetime

from models import *
from services.job_scraper import *
from services.job_matcher import calculate_match
from services.resume_parser import extract_resume_text

from schedular import start_scheduler
from mailer import *

from recommendation import get_recommendations
from mailer import mail
from cleanup_job import delete_old_jobs
from job_alert import send_daily_alerts
import os
import json

load_dotenv()


app = Flask(__name__)

# read db url from.env
database_url = os.getenv("DATABASE_URL")


# configiration
app.config["SECRET_KEY"] = "this_is_my_secret_key_123"
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_pre_ping": True,   # tests each connection before using it
    "pool_recycle": 280,     # recycles connections before they go stale
}


app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("Username")
app.config["MAIL_USERNAME"] = os.getenv("Gmail")
app.config["MAIL_PASSWORD"] =os.getenv("Mailpassword")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("Username")

mail.init_app(app)

# initialize extension
db.init_app(app)


# load manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"




# user loader
@login_manager.user_loader
def loaduser(user_id):
     return db.session.get(User ,int(user_id))

# create table
with app.app_context():
     db.create_all()


# register route
@app.route("/register", methods=["GET", "POST"])
def register():

    # already logged in
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # email already exists
        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:
            return "Email already exists"

        hashed_password = generate_password_hash(
            password
        )

        user = User(
            username=username,
            email=email,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        login_user(user)

        return redirect(url_for("profile"))

    return render_template("register.html")

# login route
@app.route("/login",methods=["GET","POST"])
def login():
    #  avoid user to see the login page if user is login
     if current_user.is_authenticated :
          return redirect("/")
     
     if request.method == "POST":
          email = request.form["email"]
          password = request.form["password"]

          user = User.query.filter_by(email=email).first()

          if user and check_password_hash(user.password,password):
               login_user(user)
               return redirect("/")
          return "Invalid Email or Password !"
     return render_template("login.html")
 
 
# home route
@app.route("/")
@login_required
def home():

    profile = CareerProfile.query.filter_by(
        user_id=current_user.id
    ).first()
    recommendations = get_recommendations(
        current_user.id
    )[:6]
    if not profile:
        return redirect(url_for("profile"))

    recommended_count = 0

    jobs = Job.query.all()

    for job in jobs:

        score, matched_skills = calculate_match(
            profile.skills,
            job.skills
        )

        if score > 0:
            recommended_count += 1

    return render_template(
        "index.html",
        jobs_count=len(jobs),
        recommended_count=recommended_count,
        recommendations=recommendations
    )

  
    
# logout route 
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

# for current year in ui footer

@app.context_processor
def inject_year():
    return {
        "current_year": datetime.now().year
    } 
    
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

    profile = CareerProfile.query.filter_by(
        user_id=current_user.id
    ).first()

    if request.method == "POST":

        if not profile:

            profile = CareerProfile(
                user_id =current_user.id
            )
            
        
        profile.target_role = request.form.get(
            "target_role"
        )

        profile.skills = request.form.get(
            "skills"
        )

        profile.location = request.form.get(
            "location"
        )

        profile.alerts_enabled= (
            request.form.get("receive_emails")
            == "on"
        )
        
        if "resume" in request.files:
            upload_resume()
        

        db.session.add(profile)

        db.session.commit()

        flash(
            "Profile Updated Successfully",
            "success"
        )

        return redirect(
            "/"
        )

    return render_template(
        "profile.html",
        profile=profile
    ) 
    
    

  
@app.route("/recommendations")
@login_required
def recommendations():

    

    recommendations = get_recommendations(
        current_user.id
    )

    

    return render_template(
        "recommendations.html",
        recommendations=recommendations
    )
    
    
@app.route("/apply/<int:job_id>")
@login_required
def apply_job(job_id):

    existing = Application.query.filter_by(
        user_id=current_user.id,
        job_id=job_id
    ).first()

    if not existing:

        application = Application(
            user_id=current_user.id,
            job_id=job_id
        )

        db.session.add(application)
        db.session.commit()

    job = Job.query.get_or_404(job_id)

    return redirect(job.apply_url)



UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/upload-resume", methods=["POST"])
@login_required
def upload_resume():

    file = request.files["resume"]

    path = os.path.join(
        "uploads",
        file.filename
    )
    os.makedirs(os.path.dirname(path), exist_ok=True)
    file.save(path)
    print("1.file saved")

    text = extract_resume_text(path)
    print("2. text extract")
    
 


    resume = Resume(
        user_id=current_user.id,
        file_name=file.filename,
        file_path=path,
        extracted_text=text,
        
    )

    db.session.add(resume)
    db.session.commit()

    return redirect(url_for("profile"))

@app.route("/fetch-jobs")
def fetch_jobs():

    

    scrape_jobs()

    return "Job Added"

@app.route("/cleanup-jobs")
def cleanup_jobs():

    delete_old_jobs(app = app)

    return "Cleanup Complete"

@app.route("/send-alerts")
def send_alerts():

    send_daily_alerts()

    return "Emails Sent"


start_scheduler(app) 
if __name__ == "__main__":
    app.run()