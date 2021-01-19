""" Base Classes for quest objects """
from __future__ import annotations

from typing import Any, Dict, ClassVar, Type
from enum import Enum
from abc import ABC, abstractmethod
from copy import deepcopy

from semver import VersionInfo  # type:  ignore

from app.game import Game
from .exceptions import QuestError, QuestLoadError


def semver_safe(start: VersionInfo, dest: VersionInfo) -> bool:
    """ whether semver loading is going to be safe """
    if start.major != dest.major:
        return False

    # check it's not a downgrade of minor version
    if start.minor > dest.minor:
        return False

    return True


class Difficulty(Enum):
    RESERVED = 0
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4
    HACKER = 5


class Quest(ABC):
    @classmethod
    def get_by_name(cls, name: str) -> Type[Quest]:
        from .quests import all_quests  # avoid circular import

        try:
            return all_quests[name]
        except KeyError as err:
            raise QuestError(f"No quest name {name}") from err

    @classmethod
    def get_first(cls) -> Type[Quest]:
        from .quests import FIRST_QUEST_KEY  # avoid circular import

        return cls.get_by_name(FIRST_QUEST_KEY)

    @classmethod
    def new(cls, game: Game) -> Quest:
        """ create a new quest whose parent is `game` """
        if not game:
            raise ValueError("Game can't be blank")

        quest = cls()
        quest.game = game

        # load data if it exists
        quest_doc = db.collection("quest").document(quest.key).get()
        if quest_doc.exists:
            quest.load(quest_doc.to_dict())

        # save data, this will upgrade version if it exists
        # TODO: handle game in progress
        quest_doc.reference.set(quest.get_save_data())

        return quest

    @property
    @abstractmethod
    def version(cls) -> VersionInfo:
        return NotImplemented

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
    NAME_KEY = "_name"
    game: Optional[Game] = None

    def __init_subclass__(self):
        self.quest_data = deepcopy(self.default_data)

    @property
    def key(self) -> str:
        if not self.game:
            raise ValueError("game parent not set")
        return f"{self.game.key}:{self.__class__.__name__}"

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
        self.quest_data[self.NAME_KEY] = str(self.__class__.__name__)
        return self.quest_data

    def __repr__(self):
        return f"{self.__class__.__name__}(game={repr(self.game)})"
