""" Setup for tests """

import pytest
import string
import random

from app.firebase_utils import db, firestore
from app.user import User, Source, find_user_by_source_id
from app.game import Game, find_game_by_user
from app.quest import Quest, DEBUG_QUEST_KEY, get_quest_by_name, get_first_quest
from app.models import UserData


@pytest.fixture
def random_id():
    """ A random alphanumeric ID for various uses in tests """
    return "".join([random.choice(string.ascii_letters) for _ in range(10)])


@pytest.fixture
def random_user():
    """ A random user for testing, does not write to database """
    user_id = "test_" + "".join(
        [random.choice(string.ascii_letters) for _ in range(10)]
    )
    return User(Source.TEST, user_id)


@pytest.fixture(scope="package")
def testing_user():
    """ A user for testing, that can have games assigned, cleans up afterwards """
    user_id = "test_" + "".join(
        [random.choice(string.ascii_letters) for _ in range(10)]
    )
    uid = user_id

    user_data = UserData(
        profileImage="",
        name="Test User",
        handle="test_user",
        id=user_id,
        accessToken="",
    )

    user = User(Source.TEST, user_id)
    user.create_with_data(uid, user_data)
    yield user

    # cleanup
    db.collection("users").document(uid).delete()
    db.collection("system").document("stats").update(
        {"players": firestore.Increment(-1)}
    )


@pytest.fixture(scope="package")
def testing_game(testing_user):
    """ A random game for testing, cleans up afterwards """
    fork_url = "url_" + "".join(
        [random.choice(string.ascii_letters) for _ in range(10)]
    )

    game = Game(testing_user)
    game.new(fork_url)
    yield game

    # cleanup
    db.collection("game").document(game.key).delete()
    db.collection("system").document("stats").update({"games": firestore.Increment(-1)})

    # cleanup auto-created quest too
    QuestClass = get_first_quest()
    quest = QuestClass(game)
    db.collection("quest").document(quest.key).delete()

    # cleanup auto-created quest too
    QuestClass = get_quest_by_name(DEBUG_QUEST_KEY)
    quest = QuestClass(game)
    db.collection("quest").document(quest.key).delete()
