from abc import ABC, abstractmethod

from ..context import AppContext
from ..qcomp import QItem

__all__ = ["QPage"]

class QPage(ABC, QItem):
    @abstractmethod
    def post_init(self, context: AppContext) -> None:
        pass