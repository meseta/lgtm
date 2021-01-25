""" Test for quest load/save handling system """

import pytest
from semver import VersionInfo  # type:  ignore

from app.quest import Quest, Difficulty, QuestDefinitionError
from app.quest.stage import DebugStage
from app.quest.loader import all_quests
from app.quest.quests.debug import DebugQuest


class BadQuest(Quest):
    version = VersionInfo.parse("1.0.0")
    description = "Bad quest for testing, it is missing stuff"


class BadStageCycle(Quest):
    version = VersionInfo.parse("1.0.0")
    difficulty = Difficulty.RESERVED
    description = "Bad quest for testing, it has malformed stages"

    class Start(DebugStage):
        children = ["Loop"]

    class Loop(DebugStage):
        """ This should form a cycle, and get flagged by test """

        children = ["Start"]


class BadStageNotExist(Quest):
    version = VersionInfo.parse("1.0.0")
    difficulty = Difficulty.RESERVED
    description = "Bad quest for testing, it has malformed stages"

    class Start(DebugStage):
        """ This references a stage that doesn't exist, and get flagged """

        children = ["Loop"]


# pylint: disable=redefined-outer-name
def test_all_quest_instantiate():
    """Instantiate all quests to check abstract base class implementation
    and stage loading
    """

    for QuestClass in all_quests.values():
        quest = QuestClass()  # should succeed if correctly implemented
        quest.load_stages()


def test_fail_instantiate():
    """ Test bad quests that fail to instantiate """

    with pytest.raises(TypeError):
        BadQuest()


def test_fail_stage():
    """ Test bad quests that fail due to stage problems """

    quest = BadStageCycle()
    with pytest.raises(QuestDefinitionError):
        quest.load_stages()

    quest = BadStageNotExist()
    with pytest.raises(QuestDefinitionError):
        quest.load_stages()


def test_quest_has_stages():
    """ Tests if quest has stages """
    stages = DebugQuest.stages
    assert len(stages)

    # check repr
    first_stage = next(iter(stages.values()))()
    assert str(first_stage)
    assert repr(first_stage)
