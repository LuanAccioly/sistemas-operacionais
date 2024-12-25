import argparse
import json
import math
import random
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from commons.process import Process, ProcessState
from commons.utils import clear_terminal
from virtual_memory.frame import Frame
from virtual_memory.page import Page

random.seed(42)


def fifo_select(processes: list[Process], clock: int) -> Process:
    selection_set = [
        p
        for p in processes
        if (p.state == ProcessState.READY) and (p.arrival_time <= clock)
    ]
    return selection_set[0]


def alloc_pages(process: Process, pages: list[Page]) -> bool:
    free_pages = list(filter(lambda p: p.is_free(), pages))
    free_size = sum(map(lambda p: p.size, free_pages))

    if free_size < process.size:
        return False

    n_pages = int(math.ceil(process.size / pages[0].size))
    for i in range(n_pages):
        assert free_pages[i].is_free()
        free_pages[i].residing_process = process

    return True


def alloc_page_to_frame(page: Page, frames: list[Frame]):
    free_frame = list(filter(lambda f: f.is_free(), frames))
    assert len(free_frame) > 0
    assert free_frame[0].is_free()
    free_frame[0].residing_page = page
    print(f"[OS] Página alocada no Frame {free_frame[0].id}.")


def random_page_substitution(page: Page, frames: list[Frame]):
    valid_frames = list(filter(lambda f: not f.os_reserved, frames))
    assert len(valid_frames) > 0
    rand_idx = random.randint(0, len(valid_frames) - 1)
    assert not valid_frames[rand_idx].os_reserved

    old_page = valid_frames[rand_idx].residing_page
    valid_frames[rand_idx].residing_page = page
    print(
        f"[OS] Página {old_page.id} substituída por {page.id} no Frame {valid_frames[rand_idx].id}."
    )


def select_random_page(process: Process, pages: list[Page]) -> Page:
    process_pages = list(filter(lambda p: p.residing_process == process, pages))
    rand_idx = random.randint(0, len(process_pages) - 1)
    return process_pages[rand_idx]


def print_pages_status(pages: list[Page], unit: str):
    sort_by_id = sorted(pages, key=lambda p: p.id)
    aux = dict()

    print("==== Páginas ====")

    for p in sort_by_id:
        print(f"\tPágina {p.id}:")

        if p.is_free():
            print(f"\t\tPágina Livre | Tamanho {p.size}{unit}")
        else:
            proc = p.residing_process
            usage = proc.size

            if usage > p.size:
                if proc.pid not in aux:
                    aux[proc.pid] = proc.size
                usage = min(p.size, aux[proc.pid])
                aux[proc.pid] -= p.size

            print(
                f"\t\tProcesso: {proc.name} (PID {proc.pid}, Tamanho {proc.size} {unit})"
            )
            print(f"\t\tUso de Memória: {usage}{unit} / {p.size}{unit}")
            print(f"\t\tFragmentação Interna: {usage < p.size}")
            print(f"\t\tMemória Não Utilizada: {p.size - usage} {unit}")


def print_frames_status(frames: list[Frame], unit: str):
    sort_by_id = sorted(frames, key=lambda p: p.id)

    print("==== Frames ====")

    for p in sort_by_id:
        print(f"\tFrame {p.id}:")

        if p.is_free():
            print(f"\t\tFrame Livre | Tamanho {p.size}{unit}")
        elif p.os_reserved:
            print(f"\t\tFrame Reservada ao SO | Tamanho {p.size}{unit}")
        else:
            page = p.residing_page
            print(f"\t\tPágina: {page.id}")
            print(f"\t\tUso de Memória: {page.size}{unit} / {p.size}{unit}")


def print_processes(processes: list[Process], unit: str, clock: int):
    processes = [p for p in processes if p.arrival_time <= clock]
    running = []
    ready = []
    exited = []

    def _print(title: str, procs: list[Process]):
        print(f"{title}:")
        for p in procs:
            print(f"\tName: {p.name} | PID: {p.pid} | Size: {p.size}{unit}")

    for p in processes:
        if p.state == ProcessState.RUNNING:
            running.append(p)
        elif p.state == ProcessState.READY:
            ready.append(p)
        else:
            exited.append(p)

    print("==== Lista de Processos ====")
    _print("RUNNING", running)
    _print("READY", ready)
    _print("EXITED", exited)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Executa o simulador de Gerenciamento de"
        " Memória considerando Paginação."
    )
    parser.add_argument(
        "virtual_memory",
        type=Path,
        help="Caminho para o JSON com informações das páginas e frames.",
    )
    parser.add_argument(
        "processes",
        type=Path,
        help="Caminho para o JSON com informações dos processos.",
    )

    args = parser.parse_args()

    virtual_memory = json.loads(args.virtual_memory.read_text(encoding="utf-8"))
    processes = json.loads(args.processes.read_text(encoding="utf-8"))
    assert (
        virtual_memory["unit"] == processes["unit"]
    ), "A unidade de memória deve ser igual para ambos arquivos."
    unit = virtual_memory["unit"]

    processes = [
        Process(
            name=f"Processo {p['id']}",
            pid=p["id"],
            size=p["size"],
            arrival_time=p["arrival_time"],
        )
        for p in processes["processes"]
    ]
    processes = sorted(processes, key=lambda p: p.arrival_time)

    size = virtual_memory["size"]
    frames = [Frame(id=i, size=size) for i in range(virtual_memory["number_of_frames"])]

    for i in range(virtual_memory["os_reserved_frames"]):
        frames[i].os_reserved = True

    pages = [Page(id=i, size=size) for i in range(virtual_memory["number_of_pages"])]

    physical_memory_size = sum(map(lambda f: f.size, frames))
    virtual_memory_size = sum(map(lambda p: p.size, pages))

    clock: int = 0
    quantum: int = 2
    page_faults = 0
    current_process_start: int = None
    current_process: Process = None

    clear_terminal()

    while True:
        if current_process is None:

            current_process = fifo_select(processes, clock)
            current_process.state = ProcessState.RUNNING
            current_process_start = clock

            if current_process not in map(lambda p: p.residing_process, pages):

                if not alloc_pages(current_process, pages):

                    processes.remove(current_process)

                    processes.append(current_process)

                    current_process.state = ProcessState.EXITED

                    print(
                        "[OS] Não foi possível alocar memória"
                        f' para o processo "{current_process.name}" '
                        f"(Tamanho: {current_process.size}{unit})."
                    )

                    current_process = None
                    current_process_start = None

        if current_process is not None:

            page = select_random_page(current_process, pages)
            print(f"[OS] Processo {current_process.pid} precisa da Página {page.id}.")

            if page not in map(lambda f: f.residing_page, frames):
                print(f"[OS] Página {page.id} não se encontra na memória física.")

                page_faults += 1

                if any(filter(lambda f: f.is_free(), frames)):

                    print(f"[OS] Existem frames livres para alocar a Página {page.id}.")
                    alloc_page_to_frame(page, frames)
                else:

                    print(
                        f"[OS] Necessária substituição para alocar a Página {page.id}."
                    )
                    random_page_substitution(page, frames)
            else:
                print(f"[OS] Página {page.id} já se encontra na memória física.")

        virtual_used_memory = sum(
            map(lambda p: p.size, filter(lambda p: not p.is_free(), pages))
        )
        physical_used_memory = sum(
            map(lambda f: f.size, filter(lambda f: not f.is_free(), frames))
        )
        virtual_memory_usage = virtual_used_memory / virtual_memory_size
        physical_memory_usage = physical_used_memory / physical_memory_size
        virtual_memory_usage *= 100
        physical_memory_usage *= 100

        print(
            f"=== Tempo: {clock} | "
            f"Uso de Memória Física: {physical_memory_usage}%"
            f" ({physical_used_memory}{unit}/ {physical_memory_size}{unit}) | "
            f"Uso de Memória Virtual: {virtual_memory_usage}% "
            f"({virtual_used_memory}{unit}/ {virtual_memory_size}{unit}) | "
            f"Page faults: {page_faults} ==="
        )

        print_pages_status(pages, unit)
        print_frames_status(frames, unit)
        print_processes(processes, unit, clock)

        res = input("Continuar? [S/n] ")
        if res.lower() == "n":
            exit(0)

        clock += 1

        if current_process is not None:
            if abs(clock - current_process_start) == 2:

                processes.remove(current_process)

                processes.append(current_process)

                current_process.state = ProcessState.READY

                current_process = None
                current_process_start = None

        clear_terminal()
