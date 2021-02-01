""" Test for quest load/save handling system """

import pytest
from semver import VersionInfo  # type:  ignore

from tick import TickType
from quest import Quest, Difficulty, QuestDefinitionError, DEBUG_QUEST_NAME
from quest.stage import DebugStage
from quest.loader import all_quests
from quest.content.debug import DebugQuest


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


def test_all_quest_instantiate(testing_quest_page):
    """Instantiate all quests to check abstract base class implementation
    and stage loading
    """

    for quest_class in all_quests.values():
        # should succeed if correctly implemented
        quest = quest_class(testing_quest_page)


def test_fail_instantiate(testing_quest_page):
    """ Test bad quests that fail to instantiate """

    with pytest.raises(TypeError):
        BadQuest(testing_quest_page)


def test_fail_stage(testing_quest_page):
    """ Test bad quests that fail due to stage problems """

    with pytest.raises(QuestDefinitionError):
        quest = BadStageCycle(testing_quest_page)

    with pytest.raises(QuestDefinitionError):
        quest = BadStageNotExist(testing_quest_page)


def test_quest_has_stages(testing_quest_page):
    """ Tests if quest has stages """
    quest = DebugQuest(testing_quest_page)

    stages = quest.stages
    assert len(stages)

    # check repr
    first_stage = next(iter(stages.values()))(quest)
    assert str(first_stage)
    assert repr(first_stage)


def test_execute(testing_quest_page):
    """ Test quest execution """

    # check we didn't start off with any completed stages
    assert not testing_quest_page.data.completed_stages

    # Debugquest is linear, so we expect to see only the start quest
    testing_quest_page.execute(TickType.FULL)
    assert len(testing_quest_page.data.completed_stages) == len(
        testing_quest_page.quest.stages
    )


def test_resume(testing_quest_page):
    """ Test quest resume """

    # manually set completed stages
    testing_quest_page.data.completed_stages = ["Start"]

    # resume
    testing_quest_page.execute(TickType.FULL)
    assert len(testing_quest_page.data.completed_stages) == len(
        testing_quest_page.quest.stages
    )


def test_done_skip(testing_quest_page):
    """ Test quest execution skipping if done """

    # check we have no completed stages
    assert not testing_quest_page.data.completed_stages
    testing_quest_page.mark_quest_complete()

    # excecution should just skip because we marked quest as complete
    testing_quest_page.execute(TickType.FULL)
    assert not testing_quest_page.data.completed_stages
