""" Test quest data """

import pytest
from app.firebase_utils import db
from app.quest import Quest, QuestError, DEBUG_QUEST_KEY
from app.quest.loader import all_quests
from app.quest.quests.debug import DebugQuest
from app.game import NoGame

# pylint: disable=redefined-outer-name
def test_quest_class_fail():
    """ Try to load a non-existant class """
    with pytest.raises(QuestError):
        Quest.get_by_name("_does not exist_")


def test_get_quest():
    """ A successful class fetch """
    QuestClass = Quest.get_by_name(DEBUG_QUEST_KEY)

    assert QuestClass == DebugQuest

    quest = QuestClass()
    assert str(quest)
    assert repr(quest)


def test_all_quest_instantiate():
    """ Instantiate all quests to check abstract base class implementation """

    for QuestClass in all_quests.values():
        QuestClass()  # should succeed if correctly implemented


def test_new_quest_fail():
    """ Failure to instantiate new quest """

    with pytest.raises(ValueError):
        DebugQuest.new(None)

    with pytest.raises(ValueError):
        DebugQuest.new("")


def test_invalid_init():
    """ Test instantiation with invalid game """
    quest = DebugQuest()

    assert quest.game is NoGame

    with pytest.raises(AttributeError):
        quest.key


def test_quest(testing_game):
    """ Test creating a valid quest """

    QuestClass = Quest.get_by_name(DEBUG_QUEST_KEY)

    # check the quest doesn't exist before
    quest = QuestClass()
    quest.game = testing_game
    testing_key = quest.key

    doc = db.collection("quest").document(testing_key).get()
    assert not doc.exists

    # create new game
    quest = QuestClass.new(testing_game)
    assert quest.key == testing_key

    # check it
    doc = db.collection("quest").document(testing_key).get()
    assert doc.exists

    # create again, this should still work, and avoid loading data
    # TODO: check for lost progress data
    quest = QuestClass.new(testing_game)
    assert quest.key == testing_key

    # cleanup
    doc.reference.delete()
