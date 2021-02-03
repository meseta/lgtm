""" Test conditional stage """

import pytest
from semver import VersionInfo  # type:  ignore
import operator

from quest import Quest, Difficulty
from quest.quest import QuestBaseModel
from quest.stage import DebugStage, ConditionStage, FinalStage


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


def test_initial_execute(testing_quest_page):
    """  Should only manage to complete 1 stage due to missing data """
    quest = TestQuestBranching(testing_quest_page)
    quest.execute()

    assert len(testing_quest_page.data.completed_stages) == 1
    assert "Start" in testing_quest_page.data.completed_stages
    assert not testing_quest_page.is_quest_complete()


def test_ending(testing_quest_page):
    """ Should run til BranchA completion """

    quest = TestQuestBranching(testing_quest_page)
    quest.quest_data.value_b = quest.quest_data.value_a
    quest.execute()

    assert testing_quest_page.is_stage_complete("BranchA")
    assert testing_quest_page.is_stage_complete("EndingA")
    assert not testing_quest_page.is_stage_complete("BranchB")
    assert not testing_quest_page.is_stage_complete("EndingB")
    assert testing_quest_page.is_quest_complete()


def test_ending2(testing_quest_page):
    """ Test for BranchB completion """

    quest = TestQuestBranching(testing_quest_page)
    quest.quest_data.value_a = 100
    quest.execute()

    assert testing_quest_page.is_stage_complete("BranchB")
    assert testing_quest_page.is_stage_complete("EndingB")
    assert not testing_quest_page.is_stage_complete("BranchA")
    assert not testing_quest_page.is_stage_complete("EndingA")
    assert testing_quest_page.is_quest_complete()
