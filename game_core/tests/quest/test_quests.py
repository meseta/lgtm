""" Test quest data """

import pytest
from app.firebase_utils import db
from app.quest import Quest, QuestError, QuestLoadError, DEBUG_QUEST_KEY
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


def test_quest_load_fail(testing_game):
    """ Test loading fail """

    QuestClass = Quest.get_by_name(DEBUG_QUEST_KEY)

    # create new game
    quest = QuestClass.new(testing_game)
    quest.save()

    # break the data
    doc_ref = db.collection("quest").document(quest.key)
    doc_ref.set({"this": "broken"})

    with pytest.raises(QuestLoadError):
        quest.load()

    # cleanup
    doc_ref.delete()


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
    quest.save()

    # check it
    doc = db.collection("quest").document(testing_key).get()
    assert doc.exists

    # create again, this should still work
    quest = QuestClass.new(testing_game)
    assert quest.key == testing_key
    quest.load()

    # cleanup
    doc.reference.delete()
