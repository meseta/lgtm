""" Tests for main.py """

import os
import json
import pytest

from pydantic import ValidationError
from functions_framework import create_app  # type: ignore

from firebase_utils import db, firestore
from github_utils import GitHubHookFork
import app.github_utils.github

from user import User, Source
from game import Game
from quest_page import QuestPage

FUNCTION_SOURCE = "app/main.py"
TEST_FILES = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "test_files",
)


class Payload:  # pylint: disable=too-few-public-methods
    """ Container for holding header/payload pairs during testing"""

    def __init__(self, header_path, payload_path):
        with open(os.path.join(TEST_FILES, header_path)) as fp:
            self.headers = json.load(fp)
        with open(os.path.join(TEST_FILES, payload_path), "rb") as fp:
            self.payload = fp.read()


@pytest.fixture()
def good_fork():
    """ A payload containing (raw) data, this is recorded from GitHub """
    return Payload("good_fork_headers.json", "good_fork.bin")


@pytest.fixture()
def bad_fork():
    """A payload containing (raw) data, that has been edited to be missing stuff
    but paired wiht a valid signature"""
    return Payload("bad_fork_headers.json", "bad_fork.bin")


@pytest.fixture()
def wrong_fork():
    """ A payload containing (raw) data, but of the wrong fork """
    return Payload("wrong_fork_headers.json", "wrong_fork.bin")


@pytest.fixture(scope="module")
def webhook_listener_client():
    """ Test client """
    return create_app("github_webhook_listener", FUNCTION_SOURCE, "http").test_client()


# pylint: disable=redefined-outer-name
def test_model(good_fork):
    """ Test that our validator works """

    hook_fork = GitHubHookFork.parse_raw(good_fork.payload)
    assert hook_fork.forkee.owner.login


def test_model_invalid(bad_fork):
    """ Test that our validator fails correctly """

    with pytest.raises(ValidationError):
        GitHubHookFork.parse_raw(bad_fork.payload)


def test_model_validation_fail(webhook_listener_client, bad_fork):
    """ Test model validation failure with bad payload but correct signature for it"""

    res = webhook_listener_client.post(
        "/", headers=bad_fork.headers, data=bad_fork.payload
    )
    assert res.status_code == 400


def test_signature_fail(webhook_listener_client, good_fork, bad_fork):
    """ Test signature validation failure with good payload but incorrect signature for it"""

    res = webhook_listener_client.post(
        "/", headers=bad_fork.headers, data=good_fork.payload
    )
    assert res.status_code == 403


def test_no_signature(webhook_listener_client, good_fork):
    """ When signatures are not supplied """

    res = webhook_listener_client.post(
        "/", headers={"Content-Type": "application/json"}, data=good_fork.payload
    )
    assert res.status_code == 403


def test_wrong_fork(webhook_listener_client, wrong_fork):
    """ For a good fork that's working fine """

    res = webhook_listener_client.post(
        "/", headers=wrong_fork.headers, data=wrong_fork.payload
    )
    assert res.status_code == 404


def test_good_fork(webhook_listener_client, good_fork):
    """ For a good fork that's working fine """

    res = webhook_listener_client.post(
        "/", headers=good_fork.headers, data=good_fork.payload
    )
    assert res.status_code == 200

    # check game got created
    user_id = json.loads(good_fork.payload)["forkee"]["owner"]["id"]
    user = User.from_source_id(Source.GITHUB, user_id)
    game = Game.from_user(user)
    quest = QuestPage.from_game_get_first_quest(game)

    assert game.exists
    assert quest.exists

    # erase quest and run again
    quest.delete()
    assert not quest.exists

    res = webhook_listener_client.post(
        "/", headers=good_fork.headers, data=good_fork.payload
    )
    assert res.status_code == 200

    assert quest.exists
