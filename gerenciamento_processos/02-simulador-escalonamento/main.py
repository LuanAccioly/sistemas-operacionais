import time


class Processo:
    def __init__(self, pid, nome, prioridade, tipo, tempo_cpu):
        self.pid = pid
        self.nome = nome
        self.prioridade = prioridade
        self.tipo = tipo
        self.tempo_cpu = tempo_cpu
        self.tempo_restante = tempo_cpu
        self.turnaround = 0
        self.tempo_espera = 0

    def __str__(self):
        return f"ID: {self.pid}, Nome: {self.nome}, Prioridade: {self.prioridade}, Tipo: {self.tipo}, Tempo CPU: {self.tempo_cpu}, Tempo Restante: {self.tempo_restante}"


class Escalonador:
    def __init__(self, quantum):
        self.processos = []
        self.quantum = quantum
        self.clock = 0

    def adicionar_processo(self, processo):
        self.processos.append(processo)

    def escalonar(self, algoritmo):
        if algoritmo == "FIFO":
            self._escalonamento_fifo()
        elif algoritmo == "RR":
            self._escalonamento_rr()
        elif algoritmo == "PRIORIDADE":
            self._escalonamento_prioridade()
        else:
            print("Algoritmo inválido!")

    def _escalonamento_fifo(self):
        print("\n[Escalonamento FIFO]")
        processos_fifo = self.processos[:]
        while processos_fifo:
            processo_atual = processos_fifo.pop(0)
            print(f"Executando: {processo_atual.nome} (ID: {processo_atual.pid})")
            tempo_execucao = processo_atual.tempo_cpu
            self.clock += tempo_execucao
            processo_atual.turnaround = self.clock
            processo_atual.tempo_espera = self.clock - processo_atual.tempo_cpu
            print(f"{processo_atual.nome} finalizou a execução.")
            self._mostrar_status(processos_fifo)
            print("\n")
            time.sleep(2)
        self.calcular_tempo_medio()

    def _escalonamento_rr(self):
        print("\n[Escalonamento Round Robin]")
        fila = self.processos[:]
        while fila:
            processo_atual = fila.pop(0)
            tempo_execucao = min(self.quantum, processo_atual.tempo_restante)
            processo_atual.tempo_restante -= tempo_execucao
            self.clock += tempo_execucao
            print(
                f"Tempo: {self.clock}ms, Executando: {processo_atual.nome} por {tempo_execucao}ms"
            )
            if processo_atual.tempo_restante > 0:
                fila.append(processo_atual)
            else:
                processo_atual.turnaround = self.clock
                processo_atual.tempo_espera = self.clock - processo_atual.tempo_cpu
                print(f"{processo_atual.nome} finalizou a execução.")
            self._mostrar_status(fila)
            print("\n")
            time.sleep(1)
        self.calcular_tempo_medio()

    def _escalonamento_prioridade(self):
        print("\n[Escalonamento por Prioridade]")
        processos_prioridade = self.processos[:]
        while processos_prioridade:
            processos_prioridade.sort(key=lambda p: p.prioridade)
            processo_atual = processos_prioridade.pop(0)
            print(
                f"Executando: {processo_atual.nome} (ID: {processo_atual.pid}, Prioridade: {processo_atual.prioridade})"
            )
            tempo_execucao = processo_atual.tempo_cpu
            self.clock += tempo_execucao
            processo_atual.turnaround = self.clock
            processo_atual.tempo_espera = self.clock - processo_atual.tempo_cpu
            print(f"{processo_atual.nome} finalizou a execução.")
            self._mostrar_status(processos_prioridade)
            print("\n")
            time.sleep(2)
        self.calcular_tempo_medio()

    def _mostrar_status(self, processos):
        print(f"Relógio: {self.clock}ms")
        for processo in processos:
            print(processo)

    def calcular_tempo_medio(self):
        total_espera = 0
        total_turnaround = 0
        for processo in self.processos:
            total_espera += processo.tempo_espera
            total_turnaround += processo.turnaround
        num_processos = len(self.processos)
        if num_processos > 0:
            print(f"Tempo Médio de Espera: {total_espera / num_processos}ms")
            print(f"Tempo Médio de Turnaround: {total_turnaround / num_processos}ms")
        else:
            print("Nenhum processo foi escalonado.")


processos = [
    Processo(pid=1, nome="Processo 1", prioridade=3, tipo="CPU", tempo_cpu=10),
    Processo(pid=2, nome="Processo 2", prioridade=2, tipo="I/O", tempo_cpu=5),
    Processo(pid=3, nome="Processo 3", prioridade=1, tipo="CPU", tempo_cpu=7),
    Processo(pid=30, nome="Processo 30", prioridade=1, tipo="I/O", tempo_cpu=7),
    Processo(pid=4, nome="Processo 4", prioridade=4, tipo="I/O", tempo_cpu=6),
]
quantum = 4

print("\n\n===================== FIFO ========================")
escalonador = Escalonador(quantum)


for processo in processos:
    escalonador.adicionar_processo(processo)

escalonador.escalonar("FIFO")

print("\n\n===================== PRIORIDADE ========================")

escalonador = Escalonador(quantum)
for processo in processos:
    escalonador.adicionar_processo(processo)

escalonador.escalonar("PRIORIDADE")

print("\n\n===================== ROUND ROBIN ========================")
escalonador = Escalonador(quantum)
for processo in processos:
    escalonador.adicionar_processo(processo)

escalonador.escalonar("RR")
