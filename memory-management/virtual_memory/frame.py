from dataclasses import dataclass

from commons.process import Process
from virtual_memory.page import Page


@dataclass
class Frame:
    id: int
    size: int
    residing_page: Page | None = None
    os_reserved: bool = False

    def is_free(self) -> bool:
        return (not self.os_reserved) and (self.residing_page is None)
