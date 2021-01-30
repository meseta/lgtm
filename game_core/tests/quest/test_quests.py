""" Test quest data """

import pytest
from app.firebase_utils import db
from app.quest import Quest, QuestError, QuestLoadError, DEBUG_QUEST_KEY
from app.quest.quests.debug import DebugQuest

# pylint: disable=redefined-outer-name
def test_quest_class_fail():
    """ Try to load a non-existant class """
    with pytest.raises(QuestError):
        Quest.get_by_name("_does not exist_")


def test_get_quest(testing_game):
    """ A successful class fetch """
    QuestClass = Quest.get_by_name(DEBUG_QUEST_KEY)

    assert QuestClass == DebugQuest

    quest = QuestClass.from_game(testing_game)
    assert str(quest)
    assert repr(quest)


def test_new_quest_fail():
    """ Failure to instantiate new quest """

    with pytest.raises(ValueError):
        DebugQuest(None)

    with pytest.raises(ValueError):
        DebugQuest("")


def test_quest_load_fail(testing_quest):
    """ Test loading fail """

    # create new game
    testing_quest.save()

    # break the data
    doc_ref = db.collection("quest").document(testing_quest.key)
    doc_ref.set({"this": "broken"})

    with pytest.raises(QuestLoadError):
        testing_quest.load()

    # cleanup
    doc_ref.delete()


def test_quest(testing_game):
    """ Test creating a valid quest """

    QuestClass = Quest.get_by_name(DEBUG_QUEST_KEY)

    # create new game
    quest = QuestClass.from_game(testing_game)

    # check the quest doesn't exist before
    assert not quest.exists()

    quest.save()

    # check it
    assert quest.exists()
