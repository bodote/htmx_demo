import time,os,logging
from flask import Flask, redirect, render_template, request, flash, Response, send_file,url_for, session

from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.github import make_github_blueprint, github
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required,current_user
import os
from contacts_model import Contact
from user_model import User
from archiver import Archiver
from typing import Self, Type, List, Optional
from werkzeug.wrappers import Response as WrapperResponse
from dotenv import load_dotenv


# Load the .env file
load_dotenv()

app:Flask = Flask(__name__)
app.secret_key = b'hypermedia rocks'

# Create or get logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

login_manager = LoginManager()
login_manager.init_app(app)

# Create handler for console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Create formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(console_handler)

# Google OAuth
google_blueprint = make_google_blueprint(
    client_id=os.environ.get('GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    scope=["https://www.googleapis.com/auth/userinfo.email", "openid" , "https://www.googleapis.com/auth/userinfo.profile"],
    redirect_to="google_callback",
)
# see: https://console.cloud.google.com/apis/credentials "OAuth 2.0 Client IDs" -> contactApp Authorized redirect URIs 
# = http://localhost:8080/login/google/authorized the "login" must be the same as the url_prefix below
app.register_blueprint(google_blueprint, url_prefix="/login")

# GitHub OAuth
github_bp = make_github_blueprint(
    client_id=os.environ.get('GITHUB_CLIENT_ID'),  # Replace with your Client ID
    client_secret=os.environ.get('GITHUB_CLIENT_SECRET'),  # Replace with your Client Secret
    redirect_to="github_callback",
)
# see https://github.com/settings/applications/1445491 Authorization callback URL
# http://localhost:8080/login/github/authorized the "login" must be the same as the url_prefix below
app.register_blueprint(github_bp, url_prefix="/login")


Contact.load_db()

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.before_request
def simulate_low_bandwidth():
    time.sleep(0.01)  # Add delay to simulate slow network

@app.route("/")
def index():
    return render_template("login.html",title="Contacts")

@app.route("/github_login")
def github_login():
    if not github.authorized:
        return redirect(url_for("github.login"))
    return redirect("/github_callback")

@app.route("/google_login")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    return redirect("/google_callback")


@app.route("/google_callback")
def google_callback():
    if not google.authorized:
        return redirect(url_for("google.login"))
    account_info = google_blueprint.session.get("/oauth2/v2/userinfo").json()
    user = User(account_info['id'])
    login_user(user)
    logger.info(f"google_callback account_info {account_info}")
    return redirect("/custom_callback")

@app.route("/github_callback")
def github_callback():
    if not github.authorized:
        return redirect(url_for("github.login"))
    account_info = github_bp.session.get("/user").json()
    user = User(account_info['id'])
    login_user(user)
    logger.info(f"github account_info {account_info}")
    return redirect("/custom_callback")

@app.route("/custom_callback")
def custom_callback():
    logger.info(f"custom_callback current_user.id  {current_user.id}")
    return f"Hello custom_callback route!"

@app.route('/login')
def login() ->  str:
    return render_template("login.html",title="Contacts")

@app.route('/contacts')
def contacts()-> str:
    page = int(request.args.get("page") or 0)

    search = request.args.get("q") 
    if search is not None and len(search.strip()) > 0:
        contact_set = Contact.search(search) 
    else:
        contact_set = Contact.all()
    if request.headers.get('HX-Trigger') == 'more' or request.headers.get('HX-Trigger') == 'search':
        return render_template("table_rows.html",title="Contacts",contact_list=contact_set,page=page,query=search)
    return render_template("index.html",title="Contacts",contact_list=contact_set,page=page,query=search)

@app.route('/contacts/count',methods=['GET'])
def contact_count()-> WrapperResponse:
    time.sleep(0.01) 
    return Response(f"Total contacts: {Contact.count()}")


@app.route('/contacts/new',methods=['GET'])
def new_contact_form()-> str:
    new_contact= Contact()
    return render_template("new.html",title="Contacts",contact=new_contact)

@app.route('/contacts/new',methods=['POST'])
def new_contact()-> WrapperResponse:
    contact = Contact()
    first_name = request.form.get('first',None)
    contact.first=first_name
    last_name = request.form.get('last',None)
    contact.last=last_name
    email = request.form.get('email',None) 
    contact.email=email
    if Contact.add_new(contact):
        return redirect("/contacts")
    else:
        return WrapperResponse(render_template("new.html",title="Contacts",contact=contact))
        
       

@app.route('/contacts/<contact_id>/view', methods=['GET'])
def view_contact(contact_id=0)-> str:
    contact = Contact.find(contact_id)
    return render_template("view.html",title="Contacts",contact=contact)

@app.route('/contacts/<contact_id>/edit', methods=['GET'])
def edit_contact(contact_id=0)-> str:
    contact = Contact.find(contact_id)
    return render_template("edit.html",title="Contacts",contact=contact)

@app.route('/contacts/verify', methods=['GET'])
def verify_email()-> str:
    email = request.args.get("email") 
    if email is None or  not Contact.is_valid_email(email):
        return render_template("emailError.html",email_error="not a valid email")
    else:
        return render_template("emailError.html",email_error="")

@app.route('/contacts/<contact_id>/edit', methods=['POST'])
def save_contact(contact_id=0)-> WrapperResponse:
    contactOpt:Optional[Contact]
    if contactOpt := Contact.find(contact_id):
        contact = contactOpt
        first_name:Optional[str] 
        if first_name:= request.form.get('first',None):
            contact.first=first_name
        last_name:Optional[str]
        if last_name:= request.form.get('last',None):
            contact.last=last_name        
        email: Optional[str]
        if email := request.form.get('email',None): 
            contact.email=email
        if Contact.save(contact):
            flash("Save was successful")
            return redirect("/contacts")
    return WrapperResponse(render_template("edit.html",title="Contacts",contact=contact))

@app.route('/contacts/<contact_id>', methods=['DELETE'])
def delete_contact(contact_id=0)-> WrapperResponse:
    Contact.delete(contact_id)
    flash("Delete was successful")
    if request.headers.get('HX-Trigger') == 'table-delete':
        return Response(status=200)
    return redirect("/contacts",303)

@app.route('/contacts', methods=['DELETE'])
def delete_marked_contacts()-> str:
    selected_rows = [int(id) for id in request.form.getlist('selected_row') ]
    for id in selected_rows:
        Contact.delete(id)
    contact_set = Contact.all()
    flash("Delete was successful")
    return render_template("table_rows.html",title="Contacts",contact_list=contact_set,page=0)

@app.route('/contacts/empty_row', methods=['GET'])
def empty_row()-> WrapperResponse:
    return Response(status=200)

@app.route('/contacts/archive', methods=['POST'])
def archive()-> str:
    archiver = Archiver.get()
    archiver.run()
    return render_template("archive-ui1.html",progress=0)

@app.route('/contacts/archive', methods=['GET'])
def archive_get_progress()-> str:
    if os.path.exists(Archiver.file_path):
        progress = int(os.path.getsize(Archiver.file_path)*100/4892 )
        logging.info(f"progress: {progress}")
        print(f"progress: {progress}")
        if progress <=96:
            return render_template("archive-ui1.html",progress=progress)
        else:
            return render_template("archive-ui-ready.html")

    return render_template("archive-ui1.html",progress=0)

@app.route('/contacts/download', methods=['GET'])
def download()-> WrapperResponse:
    if os.path.exists(Archiver.file_path):
        return send_file(Archiver.file_path, "archive.json", as_attachment=True)
    return Response(status=404)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
    