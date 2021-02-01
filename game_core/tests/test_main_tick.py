""" Tests for main.py """

import pytest
import json
from base64 import b64encode

from functions_framework import create_app  # type: ignore
from tick import TickEvent, TickType

FUNCTION_SOURCE = "app/main.py"


@pytest.fixture(scope="module")
def tick_client():
    """ Tick clietn """
    return create_app("tick", FUNCTION_SOURCE, "event").test_client()


@pytest.fixture
def tick_payload():
    """ Payload for tick """
    data = TickEvent(tick_type=TickType.FULL).json()
    return {
        "context": {
            "eventId": "some-eventId",
            "timestamp": "some-timestamp",
            "eventType": "some-eventType",
            "resource": "some-resource",
        },
        "data": {"data": b64encode(data.encode()).decode()},
    }


# pylint: disable=redefined-outer-name
def test_bad_payload(tick_client, tick_payload):
    """ Test a bad payload """
    tick_payload["data"]["data"] = b64encode('{"a": 1}'.encode()).decode()
    res = tick_client.post("/", json=tick_payload)
    assert res.status_code != 200


def test_tick(tick_client, tick_payload, testing_quest_page):
    """ Test tick """

    # create new game
    testing_quest_page.save()

    # load it
    assert testing_quest_page.exists
    assert not testing_quest_page.is_quest_complete()

    res = tick_client.post("/", json=tick_payload)
    assert res.status_code == 200

    # check if it's complete now
    testing_quest_page.load()
    assert testing_quest_page.is_quest_complete()
    assert len(testing_quest_page.data.completed_stages) == len(
        testing_quest_page.quest.stages
    )
