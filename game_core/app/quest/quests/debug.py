""" The intro quest """

from typing import TYPE_CHECKING

from pydantic import BaseModel
from semver import VersionInfo  # type:  ignore
from ..quest import Quest, Difficulty



class DebugQuest(Quest):
    version = VersionInfo.parse("1.0.0")
    difficulty = Difficulty.RESERVED
    description = "This is a quest to facilitate testing/debugging"

    class QuestDataModel(BaseModel):
        a: int

    default_data = QuestDataModel(a=1)


if TYPE_CHECKING:  # pragma: no cover
    DebugQuest()
