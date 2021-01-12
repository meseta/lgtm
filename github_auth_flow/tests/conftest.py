""" Setup for tests """

import pytest
from functions_framework import create_app  # type: ignore

FUNCTION_SOURCE = "app/main.py"

@pytest.fixture(scope="package")
def client():
    """ Test client """
    return create_app("github_auth_flow", FUNCTION_SOURCE).test_client()
