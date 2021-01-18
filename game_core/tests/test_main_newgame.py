""" Tests for main.py """

import string
import random
import pytest

from app.quest_system import FIRST_QUEST_NAME
from app.utils.models import NewGameData
from app.utils.db_ids import create_game_id, create_quest_id

SOURCE = "test"

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


def test_validation_fail(new_game_client, event):
    """ Event payload validation fail """

    event["data"] = {"this": "data is incorrect"}

    res = new_game_client.post("/", json=event)
    assert res.status_code == 500


@pytest.fixture
def event():
    """ Structure neede for pubsub event """
    return {
        "context": {
            "eventId": "some-eventId",
            "timestamp": "some-timestamp",
            "eventType": "some-eventType",
            "resource": "some-resource",
        },
        "data": {},
    }


@pytest.fixture
def new_game_data(firestore_client, event):
    uid = "test_user_" + "".join(
        [random.choice(string.ascii_letters) for _ in range(6)]
    )

    # create user data
    event["data"] = NewGameData(
        source=SOURCE,
        userId=uid,
        userUid=uid,
        forkUrl="test_url",
    ).dict()

    yield event

    # cleanup
    game_id = create_game_id(SOURCE, uid)
    quest_id = create_quest_id(game_id, FIRST_QUEST_NAME)
    firestore_client.collection("game").document(game_id).delete()
    firestore_client.collection("quest").document(quest_id).delete()


def test_fail_quest(firestore_client, new_game_client, new_game_data):
    """ Test situation where quest creation fails """

    # check game and quest does not exist
    game_id = create_game_id(SOURCE, new_game_data["data"]["userId"])
    quest_id = create_quest_id(game_id, FIRST_QUEST_NAME)

    firestore_client.collection("quest").document(quest_id).set({"_version": "999.9.9"})

    # create!
    res = new_game_client.post("/", json=new_game_data)
    assert res.status_code == 500


def test_game_creation(firestore_client, new_game_client, new_game_data):
    """ Test successful game creation flow """

    # check game and quest does not exist
    game_id = create_game_id(SOURCE, new_game_data["data"]["userId"])
    quest_id = create_quest_id(game_id, FIRST_QUEST_NAME)

    game = firestore_client.collection("game").document(game_id).get()
    assert not game.exists
    quest = firestore_client.collection("quest").document(quest_id).get()
    assert not quest.exists

    # create!
    res = new_game_client.post("/", json=new_game_data)
    assert res.status_code == 200

    # check if game actually created, and that it contains data
    game = firestore_client.collection("game").document(game_id).get()
    assert game.exists
    game_dict = game.to_dict()
    assert game_dict.items() >= new_game_data["data"].items()

    # check if quest was created and that it contains data
    quest = firestore_client.collection("quest").document(quest_id).get()
    assert quest.exists

    # try create again, sohuld still work, but be idempotent
    res = new_game_client.post("/", json=new_game_data)
    assert res.status_code == 200
