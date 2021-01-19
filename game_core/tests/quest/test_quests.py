""" Test quest data """

import pytest
from app.quest import Quest, QuestError, DEBUG_QUEST_KEY
from app.quest.quests import all_quests
from app.quest.quests.debug import DebugQuest

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


def test_invalid_game():
    """ Test instantiation with invalid game """
    quest = DebugQuest()

    with pytest.raises(ValueError):
        quest.key


# def test_quest():
#     """ Test creating a valid quest """

#     game = ...
#     QuestClass = Quest.get_first()
#     quest = QuestClass(game)

#     assert quest.key

#     # create again, this should still work, and avoid loading data
#     quest = QuestClass(game)
