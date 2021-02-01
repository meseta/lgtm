""" A quest for debugging purposes """

from semver import VersionInfo  # type:  ignore
from ..quest import Quest, Difficulty, QuestBaseModel
from ..stage import DebugStage, FinalStage


class DebugQuest(Quest):
    class QuestDataModel(QuestBaseModel):
        a: int = 1

    version = VersionInfo.parse("1.0.0")
    difficulty = Difficulty.RESERVED
    description = "This is a quest to facilitate testing/debugging"

    class Start(DebugStage):
        children = ["First"]

    class First(DebugStage):
        children = ["Second"]

    class Second(FinalStage):
        pass
