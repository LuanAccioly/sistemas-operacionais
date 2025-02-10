import os
import random

from classes.directory import Directory
from classes.file import File


class FileSystem:
    def __init__(self, total_blocks, block_size):
        self.total_blocks = total_blocks
        self.block_size = block_size
        self.memory = [
            {} for _ in range(total_blocks)
        ]  # Cada bloco pode armazenar múltiplos arquivos
        self.block_links = [-1] * total_blocks  # Lista encadeada dos blocos
        self.root = Directory("/")
        self.current_directory = self.root

    def allocate_blocks(self, file):
        required_blocks = (file.size + self.block_size - 1) // self.block_size
        free_blocks = [i for i, block in enumerate(self.memory) if not block]

        if len(free_blocks) < required_blocks:
            print("Erro: Espaço insuficiente!")
            return False

        allocated = random.sample(free_blocks, required_blocks)
        allocated.sort()

        for i in range(len(allocated) - 1):
            self.block_links[allocated[i]] = allocated[i + 1]  # Encadeamento

        for block in allocated:
            self.memory[block][file.name] = min(self.block_size, file.size)
            file.size -= self.block_size
            file.blocks.append(block)

        return True

    def create_file(self, name, size):
        if (
            name in self.current_directory.files
            or name in self.current_directory.subdirectories
        ):
            print("Erro: Nome já existe!")
            return

        new_file = File(name, size)
        if self.allocate_blocks(new_file):
            self.current_directory.files[name] = new_file
            print(f"Arquivo '{name}' criado.")

    def delete_file(self, name):
        if name not in self.current_directory.files:
            print("Erro: Arquivo não encontrado!")
            return

        file = self.current_directory.files[name]
        for block in file.blocks:
            del self.memory[block][name]
            self.block_links[block] = -1  # Removendo encadeamento

        del self.current_directory.files[name]
        print(f"Arquivo '{name}' removido.")

    def create_directory(self, name):
        if (
            name in self.current_directory.files
            or name in self.current_directory.subdirectories
        ):
            print("Erro: Nome já existe!")
            return

        new_directory = Directory(name, self.current_directory)
        self.current_directory.subdirectories[name] = new_directory
        print(f"Diretório '{name}' criado.")

    def delete_directory(self, name):
        if name not in self.current_directory.subdirectories:
            print("Erro: Diretório não encontrado!")
            return

        directory = self.current_directory.subdirectories[name]
        if directory.files or directory.subdirectories:
            print("Erro: Diretório não está vazio!")
            return

        del self.current_directory.subdirectories[name]
        print(f"Diretório '{name}' removido.")

    def list_directory(self):
        print("Arquivos:", list(self.current_directory.files.keys()))
        print("Diretórios:", list(self.current_directory.subdirectories.keys()))

    def show_allocation(self):
        print("Estado da memória:")
        for i, block in enumerate(self.memory):
            if block:
                next_block = (
                    self.block_links[i] if self.block_links[i] != -1 else "None"
                )
                print(f"Bloco {i}: {block}, Próximo: {next_block}")
            else:
                print(f"Bloco {i}: Vazio")

    def change_directory(self, name):
        if name == "..":
            if self.current_directory.parent:
                self.current_directory = self.current_directory.parent
        elif name in self.current_directory.subdirectories:
            self.current_directory = self.current_directory.subdirectories[name]
        else:
            print("Erro: Diretório não encontrado!")

    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def show_tree(self, directory=None, indent="  "):
        if directory is None:
            directory = self.root

        print(indent + ("/" if directory.name == "/" else directory.name + "/"))
        for subdir in directory.subdirectories.values():
            self.show_tree(subdir, indent + "  ")
        for file in directory.files.values():
            print(indent + "  " + file.name)
