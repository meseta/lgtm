from copy import deepcopy
from typing import Any, Dict, ClassVar
from abc import ABC, abstractmethod
from enum import Enum
from semver import VersionInfo  # type:  ignore

from .exceptions import QuestLoadError


class Difficulty(Enum):
    RESERVED = 0
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4
    HACKER = 5


def semver_safe(start: VersionInfo, dest: VersionInfo) -> bool:
    """ whether semver loading is going to be safe """
    if start.major != dest.major:
        return False

    # check it's not a downgrade of minor version
    if start.minor > dest.minor:
        return False

    return True


class Quest(ABC):
    @property
    @abstractmethod
    def version(cls) -> VersionInfo:
        ...

    @property
    @abstractmethod
    def difficulty(cls) -> Difficulty:
        return NotImplemented

    @property
    @abstractmethod
    def description(cls) -> str:
        return NotImplemented

    default_data: ClassVar[Dict[str, Any]] = {}
    quest_data: Dict[str, Any] = {}
    VERSION_KEY = "_version"

    def __init_subclass__(self):
        self.quest_data = deepcopy(self.default_data)

    def load(self, save_data: Dict[str, Any]) -> None:
        """ Load save data back into structure """

        # check save version is safe before upgrading
        save_semver = VersionInfo.parse(save_data[self.VERSION_KEY])
        if not semver_safe(save_semver, self.version):
            raise QuestLoadError(
                f"Unsafe version mismatch! {save_semver} -> {self.version}"
            )

        self.quest_data.update(save_data)

    def get_save_data(self) -> Dict[str, Any]:
        """ Updates save data with new version and output """

        self.quest_data[self.VERSION_KEY] = str(self.version)
        return self.quest_data
