""" Test for quest load/save handling system """

import pytest
from app.quest.quests.debug import DebugQuest

# pylint: disable=redefined-outer-name
def test_quest_has_stages():
    """ Tests if quest has stages """
    stages = DebugQuest.stages
    assert len(stages)

    # check repr
    first_stage = next(iter(stages.values()))()
    assert str(first_stage)
    assert repr(first_stage)