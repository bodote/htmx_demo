import json, copy, re

# ========================================================
# Contact Model
# ========================================================
PAGE_SIZE = 100

class Contact:
    # mock contacts database
    db = {}

    def __init__(self, id_=None, first=None, last=None, phone=None, email=None):
        self.id = id_
        self.first = first
        self.last = last
        self.phone = phone
        self.email = email
        self.errors = {}
    @staticmethod
    def is_valid_email(email):
        # This regex pattern checks for a basic email format:
        # - One or more characters for the local part (before @)
        # - @ symbol
        # - One or more characters for the domain name
        # - A dot followed by two or more characters for the top-level domain
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if email is not None and re.match(pattern, email):
            return True
        else: 
            return False

    def validate(self):
        if self.first is None or len(self.first.strip()) == 0 :
            self.errors['first']="First name must not be empty"
            return False
       
        if self.last is None  or len(self.last.strip()) == 0:
            self.errors['last']="Last name must not be empty"
            return False
       
        if self.email is None  or len(self.email.strip()) == 0:
            self.errors['email']='email must not be empty'
            return False
        if not Contact.is_valid_email(self.email) :
            return False
        return True

    @classmethod
    def load_db(cls):
        with open('contacts.json', 'r') as contacts_file:
            contacts = json.load(contacts_file)
            cls.db.clear()
            for c in contacts:
                cls.db[c['id']] = Contact(c['id'], c['first'], c['last'], c['phone'], c['email'])
    @classmethod
    def all(cls):
        return list(cls.db.values())
    
    @classmethod
    def search(cls,text):
        result =[]
        for contact in cls.db.values():
            match_first = contact.first is not None and text in contact.first
            match_last = contact.last is not None and text in contact.last
            match_email = contact.email is not None and text in contact.email
            if match_first or match_last or match_email:
                result.append(contact)
        return result
    
    @classmethod
    def findByEmail(cls,email):
        result =[]
        for contact in cls.db.values():
            match_email = contact.email is not None and email is not None and contact.email.strip() == email.strip() 
            if  match_email:
                return contact.id
        return None
    
    @classmethod
    def add_new(cls,contact):
        if not contact.validate():
            return False
        if cls.findByEmail(contact.email):
            contact.errors['email']="email already used"
            return False
        sorted_keys = sorted(cls.db)
        last_key = sorted_keys[-1]
        contact.id = last_key+1
        cls.db[contact.id] = Contact(contact.id, contact.first, contact.last, contact.phone, contact.email)
        return True

    @classmethod
    def find(cls,contact_id):
        id = int(contact_id)
        if id in  cls.db:
            return copy.copy(cls.db[id])
        else: 
            return None
    
    @classmethod
    def save(cls,contact):
        if contact.validate():
            cls.db[int(contact.id)]=contact
            return True
        else:
            return False

    @classmethod
    def delete(cls,contact_id):
        del cls.db[int(contact_id)]
        return
    
    @classmethod
    def count(cls):
        return len(cls.db.keys())
    
    def to_dict(self):
        return {
            'id': self.id,
            'first': self.first,
            'last': self.last,
            'phone': self.phone,
            'email': self.email
        }

