import argparse
from pathlib import Path
import json
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from commons.utils import clear_terminal
from commons.process import Process, ProcessState
from fixed_partition.partition import Partition


def fifo_select(processes: list[Process], clock: int) -> Process:
    selection_set = [
        p
        for p in processes
        if (p.state == ProcessState.READY) and (p.arrival_time <= clock)
    ]
    return selection_set[0]


def alloc_mem(process: Process, partitions: list[Partition]) -> bool:
    for partition in partitions:
        if partition.is_free() and partition.size >= process.size:
            partition.residing_process = process
            print(
                f'[MEMORY] Swap-in do processo "{partition.residing_process.name}" na Partição {partition.id}'
            )
            return True

    return False


def any_swap_out(process: Process, partitions: list[Partition]) -> int | None:
    candidates = [
        part
        for part in partitions
        if (not part.os_reserved) and (part.size >= process.size)
    ]

    if any(candidates):
        return candidates[0].id

    return None


def swap_out(partition_id: int, partitions: list[Partition]):
    partition = [p for p in partitions if p.id == partition_id]
    assert len(partition) == 1
    partition = partition[0]

    print(
        f'[MEMORY] Swap-out do processo "{partition.residing_process.name}" na Partição {partition.id}'
    )
    assert partition.residing_process is not None
    partition.residing_process = None


def print_partition_status(partitions: list[Partition], unit: str):
    sort_by_id = sorted(partitions, key=lambda p: p.id)

    print("==== Partições ====")

    for p in sort_by_id:
        print(f"\tPartição {p.id}:")

        if p.is_free():
            print(f"\t\tPartição Livre | Tamanho {p.size}{unit}")
        elif p.os_reserved:
            print(f"\t\tPartição Reservada ao SO | Tamanho {p.size}{unit}")
        else:
            proc = p.residing_process
            print(f"\t\tProcesso: {proc.name} (PID {proc.pid})")
            print(f"\t\tUso de Memória: {proc.size}{unit} / {p.size}{unit}")
            print(f"\t\tFragmentação Interna: {proc.size < p.size}")
            print(f"\t\tMemória Não Utilizada: {p.size - proc.size} {unit}")


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
        " Memória considerando Partições de Tamanho Fixo."
    )
    parser.add_argument(
        "partitions",
        type=Path,
        help="Caminho para o JSON com informações das partições da memória.",
    )
    parser.add_argument(
        "processes",
        type=Path,
        help="Caminho para o JSON com informações dos processos.",
    )

    args = parser.parse_args()

    partitions = json.loads(args.partitions.read_text(encoding="utf-8"))
    processes = json.loads(args.processes.read_text(encoding="utf-8"))
    assert (
        partitions["unit"] == processes["unit"]
    ), "A unidade de memória deve ser igual para ambos arquivos."
    unit = partitions["unit"]

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

    partitions = [
        Partition(id=i, size=p["size"], os_reserved="os" in p)
        for i, p in enumerate(partitions["partitions"])
    ]
    assert len(list(filter(lambda p: p.os_reserved, partitions))) == 1, (
        "Apenas uma partição pode ser reservada ao SO: %s" % partitions
    )
    memory_size = sum(map(lambda p: p.size, partitions))

    clock: int = 0
    quantum: int = 2
    current_process_start: int = None
    current_process: Process = None

    clear_terminal()

    while True:
        if current_process is None:

            current_process = fifo_select(processes, clock)
            current_process.state = ProcessState.RUNNING
            current_process_start = clock

            if current_process not in map(lambda p: p.residing_process, partitions):
                if not alloc_mem(current_process, partitions):

                    partition_id = any_swap_out(current_process, partitions)
                    if partition_id is not None:

                        swap_out(partition_id, partitions)

                        assert alloc_mem(current_process, partitions)
                    else:

                        processes.remove(current_process)

                        processes.append(current_process)

                        current_process.state = ProcessState.EXITED

                        print(
                            "[OS-ERROR] Não foi possível alocar memória"
                            f' para o processo "{current_process.name}" '
                            f"(Tamanho: {current_process.size}{unit})."
                        )

                        current_process = None
                        current_process_start = None

        used_memory = sum(
            map(lambda p: p.size, filter(lambda p: not p.is_free(), partitions))
        )
        memory_usage = used_memory / memory_size
        memory_usage *= 100
        print(
            f"=== Tempo: {clock} | Uso de Memória: {memory_usage}%"
            f" ({used_memory}{unit}/ {memory_size}{unit}) ==="
        )

        print_partition_status(partitions, unit)
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
