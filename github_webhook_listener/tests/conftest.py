# pylint: disable=redefined-outer-name,missing-function-docstring,missing-module-docstring

import os
import string
import random
import pytest


@pytest.fixture(scope="package")
def source():
    """ Source of the functions, used for loading functions """
    return os.environ["FUNCTION_SOURCE"]


@pytest.fixture
def random_id():
    """ Create a random ID for various purposes """
    return "".join([random.choice(string.ascii_letters) for _ in range(10)])
