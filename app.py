from flask import Flask , render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)



database_url = os.getenv("DATABASE_URL")

if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    stage = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.String(300),nullable=True)

with app.app_context():
    db.create_all()
    
@app.route('/' , methods=["GET","POST"])
def home():
    global id
    if request.method == "POST":

       company_name = request.form["company_name"]
       status = request.form["status"]
       stage = request.form["stage"]
       notes = request.form.get("notes")

       new_application = Application(
                      company_name=company_name,
                      status=status,
                      stage=stage,
                      notes=notes
                    )

       db.session.add(new_application)
       db.session.commit()
    
    applications = Application.query.all()
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

         else:
              rejected_count += 1

    return render_template(
            "index.html",
            applications=applications,
            applied_count=applied_count,
            interview_count=interview_count,
            selected_count=selected_count,
            rejected_count=rejected_count
        )
@app.route("/delete/<int:del_id>")
def delete(del_id):
    application = db.session.get(Application,del_id)
    if application:
           db.session.delete(application)
           db.session.commit()

    return redirect("/")

@app.route("/edit/<int:edt_id>", methods=["GET","POST"])
def edit(edt_id):

    application = db.session.get(Application, edt_id)

    if request.method == "POST":

        application.status = request.form["status"]
        application.stage = request.form["stage"]
        application.notes = request.form.get("notes")

        db.session.commit()

        return redirect("/")

    return render_template(
        "edit.html",
        application=application
    )

    
   

if __name__ == "__main__":
    app.run()