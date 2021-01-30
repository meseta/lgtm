""" Test for quest load/save handling system """

import pytest
from semver import VersionInfo  # type:  ignore
import operator

from app.tick import TickType
from app.quest import Quest, Difficulty
from app.quest.quest import QuestBaseModel
from app.quest.stage import DebugStage, ConditionStage, FinalStage


class TestQuestBranching(Quest):
    class QuestDataModel(QuestBaseModel):
        value_a: int = 1
        value_b: int = 2

    version = VersionInfo.parse("1.0.0")
    difficulty = Difficulty.RESERVED
    description = "This is a quest to test branching"

    class Start(DebugStage):
        children = ["BranchA", "BranchB"]

    class BranchA(ConditionStage):
        children = ["EndingA"]
        variable = "value_a"
        compare_variable = "value_b"

    class BranchB(ConditionStage):
        children = ["EndingB"]
        variable = "value_a"
        operator = operator.gt
        compare_value = 10

    class EndingA(FinalStage):
        children = []

    class EndingB(FinalStage):
        children = []


# pylint: disable=redefined-outer-name
def test_initial_execute(testing_game):
    """  Should only manage to complete 1 stage due to missing data """
    quest = TestQuestBranching.from_game(testing_game)

    print(quest.completed_stages)
    quest.execute_stages(TickType.FULL)

    assert len(quest.completed_stages) == 1
    assert "Start" in quest.completed_stages
    assert not quest.complete


def test_ending(testing_game):
    """ Should run til BranchA completion """

    quest = TestQuestBranching.from_game(testing_game)
    quest.quest_data.value_b = quest.quest_data.value_a
    quest.execute_stages(TickType.FULL)

    assert "BranchA" in quest.completed_stages
    assert "EndingA" in quest.completed_stages
    assert "BranchB" not in quest.completed_stages
    assert quest.complete


def test_ending2(testing_game):
    """ Test for BranchB completion """

    quest = TestQuestBranching.from_game(testing_game)
    quest.quest_data.value_a = 100
    quest.execute_stages(TickType.FULL)

    assert "BranchB" in quest.completed_stages
    assert quest.complete
