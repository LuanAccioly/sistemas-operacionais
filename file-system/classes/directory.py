class Directory:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.files = []
        self.subdirectories = {}

    def __str__(self):
        return f"Diretório: {self.path}/{self.name}"

    def add_file(self, file):
        self.files.append(file)

    def remove_file(self, file_name):
        self.files = [f for f in self.files if f.name != file_name]

    def add_subdirectory(self, directory):
        self.subdirectories[directory.name] = directory

    def remove_subdirectory(self, dir_name):
        del self.subdirectories[dir_name]
