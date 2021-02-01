""" The intro quest """

from typing import List
from pydantic import BaseModel
from semver import VersionInfo  # type:  ignore
from ..quest import Quest, Difficulty
from ..stage import DebugStage


class IntroQuest(Quest):
    class QuestDataModel(BaseModel):
        ...

    version = VersionInfo.parse("0.1.0")
    difficulty = Difficulty.BEGINNER
    description = "The intro quest"

    class Start(DebugStage):
        children: List[str] = []
