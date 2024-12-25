from dataclasses import dataclass

from commons.process import Process


@dataclass
class Partition:
    id: int
    size: int
    residing_process: Process | None = None
    os_reserved: bool = False

    def is_free(self) -> bool:
        return (not self.os_reserved) and (self.residing_process is None)

    def has_internal_fragmentation(self) -> bool:
        if self.is_free():
            return False

        return self.residing_process.size < self.size
