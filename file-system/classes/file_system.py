import os
import random

from classes.directory import Directory
from classes.file import File


class FileSystem:
    def __init__(self, total_blocks, block_size):
        self.total_blocks = total_blocks
        self.block_size = block_size
        self.memory = [None] * total_blocks  # Simula os blocos de armazenamento
        self.root = Directory("/", "")
        self.current_directory = self.root

    def allocate_blocks(self, size):
        required_blocks = (size + self.block_size - 1) // self.block_size
        free_blocks = [i for i, block in enumerate(self.memory) if block is None]

        if len(free_blocks) < required_blocks:
            print("Erro: Espaço insuficiente!")
            return None

        allocated = random.sample(free_blocks, required_blocks)
        for i in range(len(allocated) - 1):
            self.memory[allocated[i]] = allocated[i + 1]
        self.memory[allocated[-1]] = None  # Último bloco aponta para None

        return allocated[0]

    def create_file(self, name, size):
        if name in [f.name for f in self.current_directory.files]:
            print("Erro: Nome já existe!")
            return

        start_block = self.allocate_blocks(size)
        if start_block is not None:
            new_file = File(name, self.current_directory.path, size, start_block)
            self.current_directory.add_file(new_file)
            print(f"Arquivo '{name}' criado em '{self.current_directory.path}'.")

    def delete_file(self, name):
        file = next((f for f in self.current_directory.files if f.name == name), None)
        if not file:
            print("Erro: Arquivo não encontrado!")
            return

        block = file.start_block
        while block is not None:
            next_block = self.memory[block]
            self.memory[block] = None
            block = next_block

        self.current_directory.remove_file(name)
        print(f"Arquivo '{name}' removido.")

    def create_directory(self, name):
        if name in self.current_directory.subdirectories:
            print("Erro: Diretório já existe!")
            return
        new_dir = Directory(
            name,
            (
                f"{self.current_directory.path}/{name}"
                if self.current_directory.path
                else name
            ),
        )
        self.current_directory.add_subdirectory(new_dir)
        print(f"Diretório '{name}' criado.")

    def delete_directory(self, name):
        if name not in self.current_directory.subdirectories:
            print("Erro: Diretório não encontrado!")
            return
        if (
            self.current_directory.subdirectories[name].files
            or self.current_directory.subdirectories[name].subdirectories
        ):
            print("Erro: Diretório não está vazio!")
            return
        self.current_directory.remove_subdirectory(name)
        print(f"Diretório '{name}' removido.")

    def list_directory(self):
        print(f"Conteúdo de '{self.current_directory.path or '/'}':")
        for dir_name in self.current_directory.subdirectories:
            print(f"[DIR] {dir_name}")
        for file in self.current_directory.files:
            print(f"[FILE] {file.name} ({file.size}B)")

    def show_allocation(self):
        print("Estado da memória:")
        for i, block in enumerate(self.memory):
            print(f"Bloco {i}: {block}")

    def change_directory(self, name):
        if name == "..":
            if self.current_directory.path:
                parent_path = "/".join(self.current_directory.path.split("/")[:-1])
                self.current_directory = (
                    self.root if not parent_path else self.get_directory(parent_path)
                )
        elif name in self.current_directory.subdirectories:
            self.current_directory = self.current_directory.subdirectories[name]
        else:
            print("Erro: Diretório não encontrado!")

    def get_directory(self, path):
        parts = path.strip("/").split("/")
        directory = self.root
        for part in parts:
            if part in directory.subdirectories:
                directory = directory.subdirectories[part]
            else:
                return None
        return directory

    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def show_tree(self, directory=None, indent=""):
        if directory is None:
            directory = self.root
        print(indent + directory.name + "/")
        for subdir in directory.subdirectories.values():
            self.show_tree(subdir, indent + "  ")
        for file in directory.files:
            print(indent + "  " + file.name)
