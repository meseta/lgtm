""" The intro quest """

from typing import TYPE_CHECKING

from pydantic import BaseModel
from semver import VersionInfo  # type:  ignore
from ..quest import Quest, Difficulty
from ..stage import CreateIssueStage


class DebugQuest(Quest):
    class QuestDataModel(BaseModel):
        a: int

    version = VersionInfo.parse("1.0.0")
    difficulty = Difficulty.RESERVED
    description = "This is a quest to facilitate testing/debugging"
    default_data = QuestDataModel(a=1)

    class Start(CreateIssueStage):
        ...


if TYPE_CHECKING:  # pragma: no cover
    DebugQuest()
