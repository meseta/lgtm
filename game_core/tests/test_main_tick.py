""" Tests for main.py """

import pytest
import json
from base64 import b64encode

from functions_framework import create_app  # type: ignore

from app.models import TickEvent

FUNCTION_SOURCE = "app/main.py"


@pytest.fixture(scope="module")
def tick_client():
    """ Tick clietn """
    return create_app("tick", FUNCTION_SOURCE, "event").test_client()


@pytest.fixture(scope="module")
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
def test_tick(tick_client, tick_payload):
    """ Test unauthenticated """
    res = tick_client.post("/", json=tick_payload)
    assert res.status_code == 200
