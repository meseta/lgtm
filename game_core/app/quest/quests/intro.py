""" The intro quest """

from typing import TYPE_CHECKING

from pydantic import BaseModel
from semver import VersionInfo  # type:  ignore
from ..quest import Quest, Difficulty


class IntroQuest(Quest):
    class QuestDataModel(BaseModel):
        ...

    version = VersionInfo.parse("0.1.0")
    difficulty = Difficulty.BEGINNER
    description = "The intro quest"
    default_data = QuestDataModel()


if TYPE_CHECKING:  # pragma: no cover
    IntroQuest()
