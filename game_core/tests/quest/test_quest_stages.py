""" Test for quest load/save handling system """

import pytest
from semver import VersionInfo  # type:  ignore

from app.quest import Quest, Difficulty, QuestDefinitionError, DEBUG_QUEST_KEY
from app.quest.stage import DebugStage
from app.quest.loader import all_quests
from app.quest.quests.debug import DebugQuest
from app.firebase_utils import db


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
        quest = QuestClass(testing_game)  # should succeed if correctly implemented
        quest.load_stages()


def test_fail_instantiate(testing_game):
    """ Test bad quests that fail to instantiate """

    with pytest.raises(TypeError):
        BadQuest(testing_game)


def test_fail_stage(testing_game):
    """ Test bad quests that fail due to stage problems """

    with pytest.raises(QuestDefinitionError):
        quest = BadStageCycle(testing_game)

    with pytest.raises(QuestDefinitionError):
        quest = BadStageNotExist(testing_game)


def test_quest_has_stages(testing_game):
    """ Tests if quest has stages """
    quest = DebugQuest(testing_game)

    stages = quest.stages
    assert len(stages)

    # check repr
    first_stage = next(iter(stages.values()))(quest)
    assert str(first_stage)
    assert repr(first_stage)


def test_execute(testing_game):
    """ Test quest execution """

    # create new debug quest and overwrite save
    quest = DebugQuest(testing_game)
    assert not quest.completed_stages

    # Debugquest is linear, so we expect to see only the start quest
    quest.execute_stages()
    assert len(quest.completed_stages) == len(quest.stages)

    # cleanup
    db.collection("quest").document(quest.key).delete()


def test_resume(testing_game):
    """ Test quest resume """

    # create new debug quest and overwrite save
    quest = DebugQuest(testing_game)
    quest.completed_stages = ["Start"]

    # resume
    quest.execute_stages()
    assert len(quest.completed_stages) == len(quest.stages)

    # cleanup
    db.collection("quest").document(quest.key).delete()


def test_done_skip(testing_game):
    """ Test quest execution skipping if done """

    # create new debug quest and overwrite save
    quest = DebugQuest(testing_game)
    assert not quest.completed_stages
    quest.complete = True

    # Debugquest is linear, so we expect to see only the start quest
    quest.execute_stages()
    assert not quest.completed_stages

    # cleanup
    db.collection("quest").document(quest.key).delete()
