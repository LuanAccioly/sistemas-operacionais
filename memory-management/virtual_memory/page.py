from dataclasses import dataclass

from commons.process import Process


@dataclass
class Page:
    id: int
    size: int
    residing_process: Process | None = None

    def is_free(self) -> bool:
        return self.residing_process is None

    def has_internal_fragmentation(self) -> bool:
        if self.is_free():
            return False

        return self.residing_process.size < self.size
