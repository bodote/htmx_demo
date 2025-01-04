import time,os,logging
from flask import (
    Flask, redirect, render_template, request, flash, Response, send_file
)
from contacts_model import Contact
from archiver import Archiver

app = Flask(__name__)
app.secret_key = b'hypermedia rocks'
Contact.load_db()

@app.before_request
def simulate_low_bandwidth():
    time.sleep(0.01)  # Add delay to simulate slow network


@app.route('/')
def index():
    return redirect("/contacts")

@app.route('/contacts')
def contacts():
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
def contact_count():
    time.sleep(0.01) 
    return Response(f"Total contacts: {Contact.count()}")


@app.route('/contacts/new',methods=['GET'])
def new_contact_form():
    new_contact= Contact()
    return render_template("new.html",title="Contacts",contact=new_contact)

@app.route('/contacts/new',methods=['POST'])
def new_contact():
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
        return render_template("new.html",title="Contacts",contact=contact)
        
       

@app.route('/contacts/<contact_id>/view', methods=['GET'])
def view_contact(contact_id=0):
    contact = Contact.find(contact_id)
    return render_template("view.html",title="Contacts",contact=contact)

@app.route('/contacts/<contact_id>/edit', methods=['GET'])
def edit_contact(contact_id=0):
    contact = Contact.find(contact_id)
    return render_template("edit.html",title="Contacts",contact=contact)

@app.route('/contacts/verify', methods=['GET'])
def verify_email():
    email = request.args.get("email") 
    if  not Contact.is_valid_email(email):
        return render_template("emailError.html",email_error="not a valid email")
    else:
        return render_template("emailError.html",email_error="")

@app.route('/contacts/<contact_id>/edit', methods=['POST'])
def save_contact(contact_id=0):

    contact = Contact.find(contact_id)
    first_name = request.form.get('first',None)
    contact.first=first_name
    last_name = request.form.get('last',None)
    contact.last=last_name
    email = request.form.get('email',None) 
    contact.email=email

    if Contact.save(contact):
        flash("Save was successful")
        return redirect("/contacts")
    else: 
        return render_template("edit.html",title="Contacts",contact=contact)

@app.route('/contacts/<contact_id>', methods=['DELETE'])
def delete_contact(contact_id=0):
    Contact.delete(contact_id)
    flash("Delete was successful")
    if request.headers.get('HX-Trigger') == 'table-delete':
        return Response(status=200)
    return redirect("/contacts",303)

@app.route('/contacts', methods=['DELETE'])
def delete_marked_contacts():
    selected_rows = [int(id) for id in request.form.getlist('selected_row') ]
    for id in selected_rows:
        Contact.delete(id)
    contact_set = Contact.all()
    flash("Delete was successful")
    return render_template("table_rows.html",title="Contacts",contact_list=contact_set,page=0)

@app.route('/contacts/empty_row', methods=['GET'])
def empty_row():
    return Response(status=200)

@app.route('/contacts/archive', methods=['POST'])
def archive():
    archiver = Archiver.get()
    archiver.run()
    return render_template("archive-ui1.html",progress=0)

@app.route('/contacts/archive', methods=['GET'])
def archive_get_progress():
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
def download():
    if os.path.exists(Archiver.file_path):
        return send_file(Archiver.file_path, "archive.json", as_attachment=True)
    return Response(status=404)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
    