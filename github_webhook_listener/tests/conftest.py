""" Setup for tests """

import os
import json
import pytest
from functions_framework import create_app  # type: ignore

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


@pytest.fixture(scope="package")
def client():
    """ Test client """
    return create_app(
        "github_webhook_listener", os.environ["FUNCTION_SOURCE"]
    ).test_client()
