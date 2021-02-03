""" Test delay stage """

import pytest
from semver import VersionInfo  # type:  ignore
from datetime import timedelta
import time

from quest import Quest, Difficulty
from quest.quest import QuestBaseModel
from quest.stage import DebugStage, DelayStage, FinalStage


class TestQuestDelay(Quest):
    version = VersionInfo.parse("1.0.0")
    difficulty = Difficulty.RESERVED
    description = "This is a quest to test delays"

    class Start(DebugStage):
        children = ["Delay"]

    class Delay(DelayStage):
        children = ["Ending"]
        delay = timedelta(seconds=1)

    class Ending(FinalStage):
        pass


def test_delay(testing_quest_page):
    """ Should run and require a delay before completion """

    quest = TestQuestDelay(testing_quest_page)
    quest.execute()

    assert testing_quest_page.is_stage_complete("Start")
    assert not testing_quest_page.is_stage_complete("Delay")
    assert not testing_quest_page.is_stage_complete("Ending")
    assert not testing_quest_page.is_quest_complete()

    quest.execute()
    assert not testing_quest_page.is_stage_complete("Delay")
    assert not testing_quest_page.is_quest_complete()

    time.sleep(1)
    quest.execute()
    assert testing_quest_page.is_stage_complete("Delay")
    assert testing_quest_page.is_stage_complete("Ending")
    assert testing_quest_page.is_quest_complete()
