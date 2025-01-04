import pytest
from contacts_model import Contact

@pytest.fixture
def init_test():
    return None

def test_init():
    contact_instance = Contact(id_=1, first="Bodo", last=None, phone=None, email=None)
    assert contact_instance.first == "Bodo"
    assert contact_instance.last == None

def test_load():
    Contact.load_db()
    assert len(Contact.all()) == 47


def test_search():
    Contact.load_db()
    found_list = Contact.search("Joe")
    assert len(found_list) == 13
    found_list = Contact.search("joe8")
    assert len(found_list) == 1

def test_add_one():
    Contact.load_db()
    assert len(Contact.all()) == 47
    new_contact = Contact(first="firstname",last="lastname",email="l@x.com")
    Contact.add_new(new_contact)
    assert  len(Contact.all()) == 48

def test_find_one():
    Contact.load_db()
    contact = Contact.find('5')
    assert contact.first == 'Joe'

def test_save_one():
    Contact.load_db()
    contact = Contact.find('5')
    contact.email = 'test@test.de'
    Contact.save(contact)
    contact = Contact.find('5')
    assert contact.email == 'test@test.de'
def test_delete_one():
    Contact.load_db()
    contact = Contact.find('5')
    Contact.delete(contact.id)
    contact_deleted = Contact.find('5')
    assert contact_deleted == None

def test_add_existing_email_as_new_one():
    Contact.load_db()
    assert Contact.findByEmail("joe@example2.com") ==3 , f"Expected to find the email" 

def test_add_unvalid_email():
    assert  Contact.is_valid_email("j@x") is False, f"Expected to find the email" 