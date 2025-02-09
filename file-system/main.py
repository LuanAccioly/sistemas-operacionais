import os
import random


class FileSystem:
    def __init__(self, total_blocks, block_size):
        self.total_blocks = total_blocks
        self.block_size = block_size
        self.memory = [None] * total_blocks  # Simula os blocos de armazenamento
        self.files = {}  # Armazena metadados dos arquivos
        self.directories = {"/": []}  # Diretórios contendo arquivos
        self.current_directory = "/"

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
        path = (
            f"{self.current_directory}/{name}"
            if self.current_directory != "/"
            else name
        )
        if path in self.files or path in self.directories:
            print("Erro: Nome já existe!")
            return

        start_block = self.allocate_blocks(size)
        if start_block is not None:
            self.files[path] = {"size": size, "start_block": start_block}
            self.directories[self.current_directory].append(path)
        print(f"Arquivo '{path}' criado.")

    def delete_file(self, name):
        path = (
            f"{self.current_directory}/{name}"
            if self.current_directory != "/"
            else name
        )
        if path not in self.files:
            print("Erro: Arquivo não encontrado!")
            return

        block = self.files[path]["start_block"]
        while block is not None:
            next_block = self.memory[block]
            self.memory[block] = None
            block = next_block

        del self.files[path]
        self.directories[self.current_directory].remove(path)
        print(f"Arquivo '{path}' removido.")

    def create_directory(self, name):
        path = (
            f"{self.current_directory}/{name}"
            if self.current_directory != "/"
            else name
        )
        if path in self.files or path in self.directories:
            print("Erro: Nome já existe!")
            return
        self.directories[path] = []
        self.directories[self.current_directory].append(path)
        print(f"Diretório '{path}' criado.")

    def delete_directory(self, name):
        path = (
            f"{self.current_directory}/{name}"
            if self.current_directory != "/"
            else name
        )
        if path not in self.directories:
            print("Erro: Diretório não encontrado!")
            return
        if self.directories[path]:
            print("Erro: Diretório não está vazio!")
            return
        del self.directories[path]
        self.directories[self.current_directory].remove(path)
        print(f"Diretório '{path}' removido.")

    def list_directory(self):
        print(
            f"Conteúdo de '{self.current_directory}':",
            self.directories[self.current_directory],
        )

    def show_allocation(self):
        print("Estado da memória:")
        for i, block in enumerate(self.memory):
            print(f"Bloco {i}: {block}")

    def change_directory(self, name):
        if name == "..":
            if self.current_directory != "/":
                self.current_directory = (
                    "/".join(self.current_directory.split("/")[:-1]) or "/"
                )
        elif name in self.directories:
            self.current_directory = name
        else:
            print("Erro: Diretório não encontrado!")

    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def show_tree(self, directory=None, indent=""):
        if directory is None:
            directory = "/"
        print(indent + directory)
        for item in self.directories.get(directory, []):
            if item in self.directories:
                self.show_tree(item, indent + "  ")
            else:
                print(indent + "  " + item)


def main():
    total_blocks = 20
    block_size = 4
    fs = FileSystem(total_blocks, block_size)

    while True:
        command = input(f"{fs.current_directory} $ ").strip().split()
        if not command:
            continue

        cmd = command[0]
        args = command[1:]

        if cmd == "mkdir" and args:
            fs.create_directory(args[0])
        elif cmd == "rmdir" and args:
            fs.delete_directory(args[0])
        elif cmd == "touch" and len(args) == 2:
            fs.create_file(args[0], int(args[1]))
        elif cmd == "rm" and args:
            fs.delete_file(args[0])
        elif cmd == "ls":
            fs.list_directory()
        elif cmd == "alloc":
            fs.show_allocation()
        elif cmd == "cd" and args:
            fs.change_directory(args[0])
        elif cmd == "clear":
            fs.clear_screen()
        elif cmd == "tree":
            fs.show_tree()
        elif cmd == "exit":
            break
        else:
            print("Comando não reconhecido.")


if __name__ == "__main__":
    main()
