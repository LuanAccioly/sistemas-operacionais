class File:
    def __init__(self, name, path, size, start_block):
        self.name = name
        self.path = path
        self.size = size
        self.start_block = start_block

    def __str__(self):
        return f"Arquivo: {self.path}/{self.name} (Tamanho: {self.size}B, Bloco inicial: {self.start_block})"
