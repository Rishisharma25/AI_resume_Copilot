from flask import Flask, render_template, request, redirect, session, flash, url_for
from ai import analyse_resume
from db import engine, Base, SessionLocal  
import models   # ✅ only this
import PyPDF2
import docx
import json
import os
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth

load_dotenv()

app = Flask(__name__)
app.secret_key = "secret123"

oauth = OAuth(app)

# Google
oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# GitHub
oauth.register(
    name='github',
    client_id=os.environ.get('GITHUB_CLIENT_ID'),
    client_secret=os.environ.get('GITHUB_CLIENT_SECRET'),
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

# LinkedIn
oauth.register(
    name='linkedin',
    client_id=os.environ.get('LINKEDIN_CLIENT_ID'),
    client_secret=os.environ.get('LINKEDIN_CLIENT_SECRET'),
    access_token_url='https://www.linkedin.com/oauth/v2/accessToken',
    authorize_url='https://www.linkedin.com/oauth/v2/authorization',
    api_base_url='https://api.linkedin.com/v2/',
    client_kwargs={'scope': 'r_liteprofile r_emailaddress'},
)

Base.metadata.create_all(bind=engine)

# Home
@app.route('/')
def home():
    if 'user' in session:
        return redirect('/dashboard')
    return redirect('/login')

#---- Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    db = SessionLocal()

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        existing_user = db.query(models.User).filter_by(email=email).first()
        if existing_user:
            db.close()
            flash("User already exists. Please log in.", "error")
            return redirect('/signup')
        
        user = models.User(email=email, password=password)
        db.add(user)
        db.commit()
        db.close()
        flash("Account created! You can now log in.", "success")
        return redirect('/login')
    
    db.close()
    return render_template('signup.html')

# login 

@app.route('/login', methods=['GET', 'POST'])
def login():
    db = SessionLocal()

    if request.method == 'POST':

        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        user = db.query(models.User).filter_by(email=email, password = password).first()
        db.close()
        if user:
            session['user'] = user.email
            flash("Logged in successfully!", "success")
            return redirect('/dashboard')
        else:
            flash("Invalid credentials. Please try again.", "error")
            return redirect('/login')
    db.close()
    return render_template('login.html')

# Forgot Password

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    db = SessionLocal()

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        new_password = request.form.get('new_password', '').strip()

        user = db.query(models.User).filter_by(email=email).first()
        if user:
            user.password = new_password
            db.commit()
            db.close()
            flash("Password updated successfully! Please log in.", "success")
            return redirect('/login')
        else:
            db.close()
            flash("Email not found. Try signing up.", "error")
            return redirect('/forgot-password')
            
    db.close()
    return render_template('forgot_password.html')

#DASHBOARD 

@app.route('/dashboard', methods = ['GET', 'POST'])

def dashboard():
    if 'user' not in session:
        return redirect('/login')
    result = None

    if request.method == "POST":
        user_goal = request.form.get('role')
        resume_text = request.form.get('resume')

        file = request.files.get('file')

        #file handling

        if file and file.filename != "":
            if file.filename.endswith('.pdf'):
                try:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() or ""
                    resume_text = text
                except Exception as e:
                    result = {'error': f'PDF error: {str(e)}'}
            
            elif file.filename.endswith('.docx'):
                try:
                    doc = docx.Document(file)
                    text = ""
                    for para in doc.paragraphs:
                        text += para.text +'\n'
                    resume_text = text
                except Exception as e:
                    result = {'error': f'Docx error: {str(e)}'}

        if not resume_text:
            db = SessionLocal()
            user = db.query(models.User).filter_by(email=session['user']).first()
            if user:
                profile = db.query(models.UserProfile).filter_by(user_id=user.id).first()
                if profile and profile.resume_data:
                    try:
                        data = json.loads(profile.resume_data)
                        resume_text = f"Name: {data.get('full_name', '')}\n"
                        resume_text += f"Contact: {data.get('contact', '')}\n"
                        resume_text += f"Summary: {data.get('summary', '')}\n"
                        resume_text += f"Experience: {data.get('experience', '')}\n"
                        resume_text += f"Education: {data.get('education', '')}\n"
                        resume_text += f"Skills: {data.get('skills', '')}\n"
                    except:
                        pass
            db.close()

        if resume_text and user_goal:
            try:
                result = analyse_resume(resume_text, user_goal)

                #save to db
                db = SessionLocal()
                user = db.query(models.User).filter_by(email=session['user']).first()
                
                report = models.Report(
                    user_id = user.id,
                    resume_text = resume_text,
                    result = json.dumps(result)
                )

                db.add(report)
                db.commit()
                db.close()

            except Exception as e:
                result = {'error': f"AI error: {str(e)}"}

    return render_template(
        "dashboard.html",
        user=session["user"],
        result=result
    )
    
# history

@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/login")
    
    db = SessionLocal()
    user = db.query(models.User).filter_by(email=session["user"]).first()

    reports = db.query(models.Report).filter_by(user_id = user.id).all()
    db.close()

    # convert JSON string > dict
    parsed_reports = []

    for r in reports:
        try:
            parsed_result = json.loads(r.result)
            if not isinstance(parsed_result, dict):
                parsed_result = {}
        except:
            parsed_result = {}
        
        parsed_reports.append({
          "id": r.id,
          "resume": r.resume_text or "No resume text provided.",
          "result": parsed_result
         })
    return render_template("history.html", reports = parsed_reports)

# Logout

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been logged out.", "success")
    return redirect("/login")

# Profile

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user" not in session:
        return redirect("/login")
        
    db = SessionLocal()
    user = db.query(models.User).filter_by(email=session["user"]).first()
    
    if not user:
        db.close()
        return redirect("/logout")

    profile = db.query(models.UserProfile).filter_by(user_id=user.id).first()
    
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "update_password":
            current_pw = request.form.get("current_password")
            new_pw = request.form.get("new_password")
            
            if user.password == current_pw:
                user.password = new_pw
                db.commit()
                flash("Password updated successfully!", "success")
            else:
                flash("Incorrect current password.", "error")
                
        elif action == "update_resume":
            resume_data = {
                "full_name": request.form.get("full_name", ""),
                "contact": request.form.get("contact", ""),
                "summary": request.form.get("summary", ""),
                "experience": request.form.get("experience", ""),
                "education": request.form.get("education", ""),
                "skills": request.form.get("skills", "")
            }
            
            if not profile:
                profile = models.UserProfile(user_id=user.id, resume_data=json.dumps(resume_data))
                db.add(profile)
            else:
                profile.resume_data = json.dumps(resume_data)
                
            db.commit()
            flash("Resume saved successfully!", "success")
            
        return redirect("/profile")
        
    resume_data = {}
    if profile and profile.resume_data:
        try:
            resume_data = json.loads(profile.resume_data)
        except:
            pass
            
    report_count = db.query(models.Report).filter_by(user_id=user.id).count()
    user_email = user.email
    db.close()
    
    return render_template("profile.html", resume_data=resume_data, report_count=report_count, user_email=user_email)

# Delete History

@app.route("/delete-history/<int:report_id>", methods=["POST"])
def delete_history(report_id):
    if "user" not in session:
        return redirect("/login")
        
    db = SessionLocal()
    user = db.query(models.User).filter_by(email=session["user"]).first()
    
    report = db.query(models.Report).filter_by(id=report_id, user_id=user.id).first()
    if report:
        db.delete(report)
        db.commit()
        flash("Report deleted successfully.", "success")
    
    db.close()
    return redirect("/history")

# OAuth Routes
@app.route('/login/<provider>')
def login_provider(provider):
    if provider == 'google':
        redirect_uri = url_for('authorize_provider', provider='google', _external=True)
        return oauth.google.authorize_redirect(redirect_uri)
    elif provider == 'github':
        redirect_uri = url_for('authorize_provider', provider='github', _external=True)
        return oauth.github.authorize_redirect(redirect_uri)
    elif provider == 'linkedin':
        redirect_uri = url_for('authorize_provider', provider='linkedin', _external=True)
        return oauth.linkedin.authorize_redirect(redirect_uri)
    return redirect('/login')

@app.route('/authorize/<provider>')
def authorize_provider(provider):
    email = None
    if provider == 'google':
        token = oauth.google.authorize_access_token()
        user_info = token.get('userinfo')
        if user_info:
            email = user_info.get('email')
            
    elif provider == 'github':
        token = oauth.github.authorize_access_token()
        resp = oauth.github.get('user/emails')
        emails = resp.json()
        for e in emails:
            if e.get('primary'):
                email = e.get('email')
                break
                
    elif provider == 'linkedin':
        token = oauth.linkedin.authorize_access_token()
        resp = oauth.linkedin.get('emailAddress?q=members&projection=(elements*(handle~))')
        data = resp.json()
        try:
            email = data['elements'][0]['handle~']['emailAddress']
        except:
            email = None

    if not email:
        flash(f"{provider.capitalize()} login failed. Could not retrieve email.", "error")
        return redirect('/login')

    # Login or register the user
    db = SessionLocal()
    user = db.query(models.User).filter_by(email=email).first()
    
    if not user:
        new_user = models.User(email=email, password="") 
        db.add(new_user)
        db.commit()
        
    session['user'] = email
    db.close()
    
    flash(f"Successfully logged in with {provider.capitalize()}!", "success")
    return redirect('/dashboard')

if __name__ == '__main__':
    app.run(debug=True)