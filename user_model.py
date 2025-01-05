from flask_login import  UserMixin

# User model for Flask-Login
class User(UserMixin):
    def __init__(self, id):
        self.id = id