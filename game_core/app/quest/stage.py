# """ Base Classes for quest stage objects """

from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from abc import ABC

if TYPE_CHECKING:
    from .quest import Quest  # pragma: no cover


class Stage(ABC):
    quest: Optional[Quest] = None

    def __repr__(self):
        return f"{self.__class__.__name__}(quest={repr(self.quest)})"


class CreateIssueStage(Stage):
    """ This stage posts a new issue to a user's fork """
