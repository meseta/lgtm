""" The intro quest """

from typing import TYPE_CHECKING
from semver import VersionInfo  # type:  ignore
from ..system import Quest, Difficulty


class DebugQuest(Quest):
    version = VersionInfo.parse("1.0.0")
    difficulty = Difficulty.RESERVED
    description = "This is a quest to facilitate testing/debugging"
    default_data = {"a": 1}


if TYPE_CHECKING:  # pragma: no cover
    DebugQuest()
