from flask_login import  UserMixin
from typing import Self, Type, List, Optional,Any

# User model for Flask-Login
class User(UserMixin):
    def __init__(self:Self, id:str) -> None:
        self.id = id