from flask import Flask , render_template,request,redirect,flash,url_for
from flask_login import LoginManager, login_user,current_user,login_required,logout_user
from werkzeug.security import generate_password_hash,check_password_hash
from dotenv import load_dotenv
from datetime import datetime
from models import *
from services.job_scraper import *
from services.job_matcher import calculate_match
from flask_mail import Mail
import os

load_dotenv()

app = Flask(__name__)

# read db url from.env
database_url = os.getenv("DATABASE_URL")

# configiration
app.config["SECRET_KEY"] = "this_is_my_secret_key_123"
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

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

    applications = Application.query.filter_by(
        user_id=current_user.id
    ).all()

    applied_count = 0
    interview_count = 0
    selected_count = 0
    rejected_count = 0

    for item in applications:

        if item.status == "Applied":
            applied_count += 1

        elif item.status == "Interview":
            interview_count += 1

        elif item.status == "Selected":
            selected_count += 1

        elif item.status == "Rejected":
            rejected_count += 1
            
       

    return render_template(
        "index.html",
        applications=applications,
        applied_count=applied_count,
        interview_count=interview_count,
        selected_count=selected_count,
        rejected_count=rejected_count,
        
    )

# delete route
@app.route("/delete/<int:application_id>")
@login_required
def delete(application_id):

    application = Application.query.get_or_404(
        application_id
    )

    if application.user_id != current_user.id:
        return redirect("/")

    db.session.delete(application)
    db.session.commit()

    return redirect("/")

# edit route
@app.route(
    "/edit/<int:application_id>",
    methods=["GET", "POST"]
)
@login_required
def edit(application_id):

    application = Application.query.get_or_404(
        application_id
    )

    if application.user_id != current_user.id:
        return redirect("/")

    if request.method == "POST":

        application.status = request.form[
            "status"
        ]

        db.session.commit()

        return redirect("/")

    return render_template(
        "edit.html",
        application=application
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

        profile.receive_emails = (
            request.form.get("receive_emails")
            == "on"
        )

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
    
    
    
@app.route("/fetch-jobs")
def fetch_jobs():

    scrape_jobs()

    return "Jobs Fetched Successfully"
  
@app.route("/recommendations")
@login_required
def recommendations():

    profile = CareerProfile.query.filter_by(
        user_id=current_user.id
    ).first()

    if not profile:
        return redirect(url_for("profile"))

    jobs = Job.query.all()

    recommendations = []
    print("Jobs in DB:", Job.query.count())
    print("Profile Skills:", profile.skills)

    for job in jobs:

        score, matched_skills = calculate_match(
            profile.skills,
            job.skills
            )

      

        recommendations.append({
            "job": job,
            "score": score,
            "matched_skills": matched_skills
            })

    recommendations.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    recommendations = recommendations[:20]

    return render_template(
        "recommendations.html",
        recommendations=recommendations
    )
    
    
@app.route("/apply/<int:job_id>")
@login_required
def apply_job(job_id):

    application = Application(
        user_id=current_user.id,
        job_id=job_id
    )

    db.session.add(application)
    db.session.commit()

    return redirect(url_for("dashboard"))





if __name__ == "__main__":
    app.run(debug=True)