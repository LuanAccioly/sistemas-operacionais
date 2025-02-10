class Directory:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.files = {}
        self.subdirectories = {}

    def get_path(self):
        if self.parent is None:
            return "/"
        return f"{self.parent.get_path()}/{self.name}".replace("//", "/")
