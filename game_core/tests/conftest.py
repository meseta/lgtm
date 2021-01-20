""" Setup for tests """

import pytest
import string
import random

from app.firebase_utils import db
from app.user import User, Source
from app.game import Game
from app.quest import Quest
from app.models import UserData


@pytest.fixture
def random_id():
    """ A random alphanumeric ID for various uses in tests """
    return "".join([random.choice(string.ascii_letters) for _ in range(10)])


@pytest.fixture
def random_user():
    """ A random user for testing, cleans up afterwards """
    uid = "test_" + "".join([random.choice(string.ascii_letters) for _ in range(10)])

    user_data = UserData(
        profileImage="", name="Test User", handle="test_user", id=uid, accessToken=""
    )

    user = User.new(uid, Source.TEST, user_data)
    yield user

    # cleanup
    db.collection("users").document(uid).delete()


@pytest.fixture(scope="package")
def testing_user():
    """ A user for testing, that can have games assigned, cleans up afterwards """
    uid = "test_" + "".join([random.choice(string.ascii_letters) for _ in range(10)])

    user_data = UserData(
        profileImage="", name="Test User", handle="test_user", id=uid, accessToken=""
    )

    user = User.new(uid, Source.TEST, user_data)
    yield user

    # cleanup
    db.collection("users").document(uid).delete()


@pytest.fixture(scope="package")
def testing_game(testing_user):
    """ A random game for testing, cleans up afterwards """
    fork_url = "url_" + "".join(
        [random.choice(string.ascii_letters) for _ in range(10)]
    )

    game = Game.new(testing_user, fork_url)
    yield game

    # cleanup
    db.collection("game").document(game.key).delete()

    # cleanup auto-created quest too
    QuestClass = Quest.get_first()
    quest = QuestClass()
    quest.game = game
    db.collection("quest").document(quest.key).delete()
