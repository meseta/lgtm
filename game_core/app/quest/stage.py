# """ Base Classes for quest stage objects """

from __future__ import annotations

from typing import Union, List, TYPE_CHECKING
from abc import ABC, abstractmethod

from .sentinels import NoQuest, NoQuestType

if TYPE_CHECKING:
    from .quest import Quest  # pragma: no cover


class Stage(ABC):
    @property
    @abstractmethod
    def children(cls) -> List[str]:
        """ List of children nodes of this stage """
        return NotImplemented

    quest: Union[Quest, NoQuestType] = NoQuest

    def __repr__(self):
        return f"{self.__class__.__name__}(quest={repr(self.quest)})"


class DebugStage(Stage):
    """ For debugging purposes """


class CreateIssueStage(Stage):
    """ This stage posts a new issue to a user's fork """
