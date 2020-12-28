""" Tests for pydantic models """

import pytest
from pydantic import ValidationError
from app.utils.models import GitHubHookFork

# pylint: disable=redefined-outer-name
def test_model(good_fork):
    """ Test that our validator works """

    hook_fork = GitHubHookFork.parse_raw(good_fork.payload)
    assert hook_fork.forkee.owner.login


def test_model_invalid(bad_fork):
    """ Test that our validator fails correctly """

    with pytest.raises(ValidationError):
        GitHubHookFork.parse_raw(bad_fork.payload)
