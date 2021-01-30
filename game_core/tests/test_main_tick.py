""" Tests for main.py """

import pytest
import json
from base64 import b64encode

from functions_framework import create_app  # type: ignore

from app.quest import Quest, DEBUG_QUEST_KEY
from app.models import TickEvent

FUNCTION_SOURCE = "app/main.py"


@pytest.fixture(scope="module")
def tick_client():
    """ Tick clietn """
    return create_app("tick", FUNCTION_SOURCE, "event").test_client()


@pytest.fixture
def tick_payload():
    """ Payload for tick """
    data = TickEvent(source="test").dict()
    return {
        "context": {
            "eventId": "some-eventId",
            "timestamp": "some-timestamp",
            "eventType": "some-eventType",
            "resource": "some-resource",
        },
        "data": {"data": b64encode(json.dumps(data).encode()).decode()},
    }


# pylint: disable=redefined-outer-name
def test_bad_payload(tick_client, tick_payload):
    """ Test a bad payload """
    tick_payload["data"]["data"] = b64encode('{"a": 1}'.encode()).decode()
    res = tick_client.post("/", json=tick_payload)
    assert res.status_code != 200


def test_tick(tick_client, tick_payload, testing_game):
    """ Test tick """

    # create new game
    QuestClass = Quest.get_by_name(DEBUG_QUEST_KEY)
    quest = QuestClass.from_game(testing_game)
    quest.save()

    # load it
    assert quest.exists()
    assert not quest.complete
    assert not quest.completed_stages

    res = tick_client.post("/", json=tick_payload)
    assert res.status_code == 200

    # check if it's complete now
    quest.load()
    assert quest.complete
    assert len(quest.completed_stages) == len(quest.stages)
