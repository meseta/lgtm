""" Tests for main.py """

import string
import random
import pytest
import os
from base64 import b64encode
import json

from app.quest_system import FIRST_QUEST_NAME
from app.utils.models import NewGameData
from app.utils.db_ids import create_game_id, create_quest_id
from functions_framework import create_app  # type: ignore

SOURCE = "test"

FUNCTION_SOURCE = "app/main.py"


@pytest.fixture(scope="module")
def new_game_post():
    """ Test client for newgame"""
    client = create_app("create_new_game", FUNCTION_SOURCE, "event").test_client()

    return lambda data: client.post(
        "/",
        json={
            "context": {
                "eventId": "some-eventId",
                "timestamp": "some-timestamp",
                "eventType": "some-eventType",
                "resource": "some-resource",
            },
            "data": {"data": b64encode(json.dumps(data).encode()).decode()},
        },
    )


# pylint: disable=redefined-outer-name
@pytest.mark.parametrize(
    "source, game_id",
    [
        ("", "abc"),
        ("abc", ""),
        (None, "abc"),
        ("abc", None),
    ],
)
def test_bad_ids(source, game_id):
    with pytest.raises(ValueError):
        create_game_id(source, game_id)
    with pytest.raises(ValueError):
        create_quest_id(source, game_id)


def test_good_ids():
    assert create_game_id("abc", "abc")
    assert create_quest_id("abc", "abc")


def test_validation_fail(new_game_post):
    """ Event payload validation fail """

    res = new_game_post({"this": "data is incorrect"})
    assert res.status_code == 500


@pytest.fixture
def new_game_data(firestore_client):
    uid = "test_user_" + "".join(
        [random.choice(string.ascii_letters) for _ in range(6)]
    )

    # create user data
    yield NewGameData(
        source=SOURCE,
        userId=uid,
        forkUrl="test_url",
    ).dict()

    # cleanup
    game_id = create_game_id(SOURCE, uid)
    quest_id = create_quest_id(game_id, FIRST_QUEST_NAME)
    firestore_client.collection("game").document(game_id).delete()
    firestore_client.collection("quest").document(quest_id).delete()


def test_fail_quest(firestore_client, new_game_post, new_game_data):
    """ Test situation where quest creation fails """

    # check game and quest does not exist
    game_id = create_game_id(SOURCE, new_game_data["userId"])
    quest_id = create_quest_id(game_id, FIRST_QUEST_NAME)

    firestore_client.collection("quest").document(quest_id).set({"_version": "999.9.9"})

    # create!
    res = new_game_post(new_game_data)
    assert res.status_code == 500


def test_game_creation(firestore_client, new_game_post, new_game_data):
    """ Test successful game creation flow """

    # check game and quest does not exist
    game_id = create_game_id(SOURCE, new_game_data["userId"])
    quest_id = create_quest_id(game_id, FIRST_QUEST_NAME)

    game = firestore_client.collection("game").document(game_id).get()
    assert not game.exists
    quest = firestore_client.collection("quest").document(quest_id).get()
    assert not quest.exists

    # create!
    res = new_game_post(new_game_data)
    assert res.status_code == 200

    # check if game actually created, and that it contains data
    game = firestore_client.collection("game").document(game_id).get()
    assert game.exists
    game_dict = game.to_dict()
    assert game_dict.items() >= new_game_data.items()

    # check if quest was created and that it contains data
    quest = firestore_client.collection("quest").document(quest_id).get()
    assert quest.exists

    # try create again, sohuld still work, but be idempotent
    res = new_game_post(new_game_data)
    assert res.status_code == 200
