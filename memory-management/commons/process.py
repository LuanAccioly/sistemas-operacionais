from enum import Enum
from dataclasses import dataclass

class ProcessState(Enum):
    READY = 'Ready'
    RUNNING = 'Running'
    EXITED = 'Exit'

@dataclass
class Process:
    name: str
    pid: int
    size: int
    arrival_time: int
    state: ProcessState = ProcessState.READY
