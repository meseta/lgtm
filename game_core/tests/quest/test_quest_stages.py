""" Test for quest load/save handling system """

import pytest
from semver import VersionInfo  # type:  ignore

from tick import TickType
from quest import Quest, Difficulty, QuestDefinitionError, DEBUG_QUEST_KEY
from quest.stage import DebugStage
from quest.loader import all_quests
from quest.quests.debug import DebugQuest


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
def test_all_quest_instantiate(testing_game):
    """Instantiate all quests to check abstract base class implementation
    and stage loading
    """

    for QuestClass in all_quests.values():
        # should succeed if correctly implemented
        quest = QuestClass.from_game(testing_game)


def test_fail_instantiate(testing_game):
    """ Test bad quests that fail to instantiate """

    with pytest.raises(TypeError):
        BadQuest.from_game(testing_game)


def test_fail_stage(testing_game):
    """ Test bad quests that fail due to stage problems """

    with pytest.raises(QuestDefinitionError):
        quest = BadStageCycle.from_game(testing_game)

    with pytest.raises(QuestDefinitionError):
        quest = BadStageNotExist.from_game(testing_game)


def test_quest_has_stages(testing_game):
    """ Tests if quest has stages """
    quest = DebugQuest.from_game(testing_game)

    stages = quest.stages
    assert len(stages)

    # check repr
    first_stage = next(iter(stages.values()))(quest)
    assert str(first_stage)
    assert repr(first_stage)


def test_execute(testing_quest):
    """ Test quest execution """

    # check we didn't start off with any completed stages
    assert not testing_quest.completed_stages

    # Debugquest is linear, so we expect to see only the start quest
    testing_quest.execute_stages(TickType.FULL)
    assert len(testing_quest.completed_stages) == len(testing_quest.stages)


def test_resume(testing_quest):
    """ Test quest resume """

    # manually set completed stages
    testing_quest.completed_stages = ["Start"]

    # resume
    testing_quest.execute_stages(TickType.FULL)
    assert len(testing_quest.completed_stages) == len(testing_quest.stages)


def test_done_skip(testing_quest):
    """ Test quest execution skipping if done """

    # check we have no completed stages
    assert not testing_quest.completed_stages
    testing_quest.complete = True

    # excecution should just skip because we marked quest as complete
    testing_quest.execute_stages(TickType.FULL)
    assert not testing_quest.completed_stages
