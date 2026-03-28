from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, name, email, profile_type="manager"):
        self.id = id
        self.name = name
        self.email = email
        self.profile_type = profile_type
    
    def is_manager(self):
        return self.profile_type == "manager"