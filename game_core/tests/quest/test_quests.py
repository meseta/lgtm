""" Test quest data """

import pytest
from app.firebase_utils import db
from app.quest import get_quest_by_name, QuestError, QuestLoadError, DEBUG_QUEST_KEY
from app.quest.quests.debug import DebugQuest

# pylint: disable=redefined-outer-name
def test_quest_class_fail():
    """ Try to load a non-existant class """
    with pytest.raises(QuestError):
        get_quest_by_name("_does not exist_")


def test_get_quest(testing_game):
    """ A successful class fetch """
    QuestClass = get_quest_by_name(DEBUG_QUEST_KEY)

    assert QuestClass == DebugQuest

    quest = QuestClass(testing_game)
    assert str(quest)
    assert repr(quest)


def test_new_quest_fail():
    """ Failure to instantiate new quest """

    with pytest.raises(ValueError):
        DebugQuest(None)

    with pytest.raises(ValueError):
        DebugQuest("")


def test_quest_load_fail(testing_game):
    """ Test loading fail """

    QuestClass = get_quest_by_name(DEBUG_QUEST_KEY)

    # create new game
    quest = QuestClass(testing_game)
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

    QuestClass = get_quest_by_name(DEBUG_QUEST_KEY)

    # check the quest doesn't exist before
    quest = QuestClass(testing_game)
    quest.game = testing_game
    testing_key = quest.key

    doc = db.collection("quest").document(testing_key).get()
    assert not doc.exists

    # create new game
    quest = QuestClass(testing_game)
    assert quest.key == testing_key
    quest.save()

    # check it
    doc = db.collection("quest").document(testing_key).get()
    assert doc.exists

    # create again, this should still work
    quest = QuestClass(testing_game)
    assert quest.key == testing_key
    quest.load()

    # cleanup
    doc.reference.delete()
