import time,os,logging
from flask import Flask, redirect, render_template, request, flash, Response, send_file,url_for, session

from flask_dance.contrib.google import make_google_blueprint
from flask_dance.contrib.github import make_github_blueprint
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
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

login_manager = LoginManager()
login_manager.init_app(app)

# Google OAuth
google_blueprint = make_google_blueprint(
    client_id=os.environ.get('GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    scope=["profile", "email"]
)
app.register_blueprint(google_blueprint, url_prefix="/google_login")

# GitHub OAuth
github_blueprint = make_github_blueprint(
    client_id=os.environ.get('GITHUB_CLIENT_ID'),
    client_secret=os.environ.get('GITHUB_CLIENT_SECRET'),
    scope="user:email"
)
app.register_blueprint(github_blueprint, url_prefix="/github_login")

Contact.load_db()

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.before_request
def simulate_low_bandwidth():
    time.sleep(0.01)  # Add delay to simulate slow network

@app.route('/')
def index() ->  WrapperResponse:
    return redirect("/contacts")


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
    