import hashlib


class Directory:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.files = {}
        self.subdirectories = {}
        self.is_protected = False
        self.password_hash = None

    def get_path(self):
        if self.parent is None:
            return "/"
        return f"{self.parent.get_path()}/{self.name}".replace("//", "/")

    def set_password(self, password):
        self.is_protected = True
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, password):
        if not self.is_protected:
            return True
        return hashlib.sha256(password.encode()).hexdigest() == self.password_hash
