import pytest,time,os, logging
from contacts_model import Contact
from archiver import Archiver
from app import contacts,app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    with app.test_client() as client:
        with app.app_context():
            # Ensure the database is loaded for testing
            Contact.load_db()
        yield client

def test_get_contracts(client):
    response = client.get('/contacts')
    assert response.status_code == 200
    assert b"<!doctype html>" in response.data, f"Expected '{response.data}' to start with '<!doctype html>'"
    assert b"Contacts" in response.data, f"Expected '{response.data}' to start with 'Contacts'"
    assert response.data.decode('utf-8').count("<tr>") <= 12, f"Expected 10 elements maximum"
    assert b"Next" in response.data,f"Expected a Next button or link"

def test_get_contracts_page2(client):
    response = client.get('/contacts?page=1')
    assert response.status_code == 200
    assert response.data.decode('utf-8').count("<tr>") <= 12, f"Expected 10 elements maximum"
    assert b"Previous" in response.data,f"Expected a Next button or link"

def test_get_contracts_more(client):
    response = client.get('/contacts?page=0', headers={'Hx-Trigger': 'more'})
    assert response.status_code == 200
    assert response.data.decode('utf-8').count("<tr>") <= 12, f"Expected 10 elements maximum"
    assert b"more" in response.data,f"Expected a Next button or link"
    assert b"<!doctype html>" not in response.data, f"Expected '{response.data}' not to to start with '<!doctype html>'"
   
def test_search_contracts(client):
    response = client.get('/contacts?q=xxx')
    assert response.status_code == 200
    assert b"<!doctype html>" in response.data, f"Expected '{response.data}' to start with '<!doctype html>'"
    assert b"Contacts" in response.data, f"Expected '{response.data}' to start with 'Contacts'"
    assert b"<td>" not in response.data, f"Expected '{response.data}' to not contain '<td>'"
    response = client.get('/contacts?q=joe8')
    assert response.status_code == 200
    assert b"<!doctype html>" in response.data, f"Expected '{response.data}' to start with '<!doctype html>'"
    assert b"Contacts" in response.data, f"Expected '{response.data}' to start with 'Contacts'"
    assert b"joe8"  in response.data, f"Expected '{response.data}' to  contain 'joe8'"

def test_get_new_contacts_form(client):
    response = client.get('/contacts/new')
    assert response.status_code == 200
    assert b"New Contact" in response.data, f"Expected '{response.data}' contain 'New Contact'"

def test_post_new_contacts_form_with_error(client):
    form_data = {
        'first':'firstName',
        'last':'lastName'
    }
    response = client.post('/contacts/new',data=form_data)
    assert response.status_code == 200
    assert b"email must not be empty" in response.data, f"Expected '{response.data}' contain 'email must not be empty'"

def test_post_new_contacts_form(client):
    form_data = {
        'first':'firstName',
        'last':'lastName',
        'email':'BodoTe@x.com'
    }
    response = client.post('/contacts/new',data=form_data)
    assert response.status_code == 302
    assert len(Contact.all()) == 48
    # assert b"email must not be empty" in response.data, f"Expected '{response.data}' contain 'email must not be empty'"

def test_get_edit_contact(client):
    contact= Contact.find(5)
    form_data ={
        'first':contact.first,
        'last':contact.last,
        'email':contact.email,
        'id':contact.id
    }
    response = client.get('/contacts/5/edit',data=form_data)
    assert response.status_code == 200
    assert b"/contacts/5/edit" in response.data, f"Expected '{response.data}' contain '/contact/5/edit'"

def test_post_edit_contact(client):
    contact= Contact.find(5)
    form_data ={
        'first':contact.first,
        'last':contact.last,
        'email':'test@test.de',
        'id':contact.id
    }
    response = client.post('/contacts/5/edit',data=form_data)
    contact_saved = Contact.find(5)
    assert 'test@test.de' == contact_saved.email
    assert response.status_code == 302
    response = client.get('/contacts')
    assert b"Save was successful" in response.data, f"Expected '{response.data}' contain 'Save was successful'"

def test_view_contact(client):
    contact= Contact.find(5)
    response = client.get('/contacts/5/view')
    assert response.status_code == 200
    assert b"joe@example.com" in response.data, f"Expected '{response.data}' contain 'joe@example.com'"

def test_verify_email(client):
    response = client.get('/contacts/verify?email=joe@example.com')
    assert response.status_code == 200, f"check valid email 'joe@example.com'"
    assert b"<span class=\"error\">" in response.data, f"Expected '{response.data}' contain '<span class=\"error\">'"

def test_verify_wrong_email(client):
    response = client.get('/contacts/verify?email=j@e')
    assert response.status_code == 200, f"check valid email 'j@e'"
    assert b"not a valid email" in response.data, f"Expected '{response.data}' contain 'not a valid email'"



def test_delete_contact(client):
    contact= Contact.find(5)
    response = client.delete('/contacts/5')
    contact_deleted = Contact.find(5)
    assert contact_deleted == None
    assert response.status_code == 303
    response = client.get('/contacts')
    assert b"Delete was successful" in response.data, f"Expected '{response.data}' contain 'Save was successful'"

def test_delete_marked(client):
    form_data ={
        'selected_row':[2,5]
    }
    assert len(Contact.all()) == 47
    response = client.delete('/contacts',data=form_data)
    assert response.status_code == 200, f"check status 200"
    assert len(Contact.all()) == 45, f"check number of contacts: 48-2=46"
    assert b"<td><input" in response.data, f"Expected new table"
    assert response.data.decode('utf-8').count("<tr") >= 11, f"Expected 11 elements "

   
def test_count(client):
    response = client.get('/contacts/count')
    assert b"Total contacts:" in response.data, f"Expected '{response.data}' contain 'Total Contacts:'"
  
def test_empty_row(client):
    response = client.get('/contacts/empty_row')
    assert response.status_code == 200, f"check status 200"

def test_archive(client):
    logging.info("file size: test starts ")
    response = client.post('/contacts/archive')
    assert response.status_code == 200, "check status 200"
    assert b"<div" in response.data, "expected a div element"
    assert b"0%" in response.data, "expected a div element"
   
    start_time = time.time()
    timeout = 10
    while not os.path.exists(Archiver.file_path):
        assert time.time() - start_time < timeout, f"Timeout waiting for archiver to start running"
        time.sleep(0.1)  # Sleep briefly to avoid busy waiting
    assert os.path.exists(Archiver.file_path), "file exists"
    start_time = time.time()
    timeout = 10
    while not os.path.getsize(Archiver.file_path)>1000:
        assert time.time() - start_time < timeout, f"Timeout waiting for archiver to start running"
        logging.info(f"file size: {os.path.getsize(Archiver.file_path)} ")
        time.sleep(0.1)
    assert os.path.getsize(Archiver.file_path)>1000, f"File {Archiver.file_path} is too small"

    response = client.get('/contacts/archive')
    assert response.status_code == 200, "check status 200"
    assert b"<div" in response.data, "expected a div element"
    assert b"0%" not in response.data, "expected a div element"

def test_download(client):
    response = client.get('/contacts/download')
     # Check that the response contains the expected headers
    assert 'Content-Disposition' in response.headers, "check Content-Disposition header"
    assert 'attachment' in response.headers['Content-Disposition'], "check attachment in Content-Disposition header"
    # Check that the response data is not empty
    assert len(response.data) > 1000, "check response data is not empty"
