from classes.file_system import FileSystem


def main():
    total_blocks = 20
    block_size = 4
    fs = FileSystem(total_blocks, block_size)

    while True:
        command = input(f"{fs.current_directory.get_path()} $ ").strip().split()
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
