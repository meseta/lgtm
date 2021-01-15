from enum import Enum
from semver import VersionInfo

from .exceptions import QuestLoadError

VERSION_KEY = "_version"


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


class Quest:
    def __init__(
        self,
        name: str,
        version: str,
        difficulty: Difficulty,
        description: str,
        default_data: dict,
    ):
        self.name = name
        self.semver = VersionInfo.parse(version)
        self.difficulty = difficulty
        self.description = description
        self.quest_data = default_data

    def load(self, save_data: dict) -> None:
        """ Load save data back into structure """

        # check save version is safe before upgrading
        save_semver = VersionInfo.parse(save_data[VERSION_KEY])
        if not semver_safe(save_semver, self.semver):
            raise QuestLoadError(
                f"Unsafe version mismatch! {save_semver} -> {self.semver}"
            )

        self.quest_data.update(save_data)

    def update_save_data(self) -> dict:
        """ Updates save data with new version and output """

        self.quest_data[VERSION_KEY] = self.semver
        return self.quest_data
