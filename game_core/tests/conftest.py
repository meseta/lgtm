""" Setup for tests """

import os
import json
import pytest
from functions_framework import create_app  # type: ignore

FUNCTION_SOURCE = "app/main.py"


@pytest.fixture(scope="package")
def client():
    """ Test client """
    # return create_app("game_core", FUNCTION_SOURCE).test_client()
