""" test character functions """

import pytest
from environs import Env
from character import ReactionType, CharacterError, character_garry

env = Env()
TEST_REPO = env("TEST_REPO")


def test_id():
    assert character_garry.user_id


def test_bad_url():
    with pytest.raises(CharacterError):
        character_garry.repo_get("repo/notexist")


def test_issue_flow(random_id):
    """All tests in one - this is desirable to minimize the number of times
    we're hitting GitHub API. So they're all combined in a single test"""
    issue_name = "Test_" + random_id

    # post it
    issue_id = character_garry.issue_post(TEST_REPO, issue_name, "This is a test post")
    assert issue_id

    # check it's not closed
    issue = character_garry.issue_get(TEST_REPO, issue_id)
    assert issue.state != "closed"

    # set an emoji on it
    character_garry.issue_reaction_create(TEST_REPO, issue_id, ReactionType.ROCKET)

    # check emojis on it
    reactions = character_garry.issue_reaction_get_from_user(
        TEST_REPO, issue_id, character_garry.user_id
    )
    assert ReactionType.ROCKET in reactions

    # create comment
    comment_id = character_garry.issue_comment_create(
        TEST_REPO, issue_id, "This is a test comment"
    )
    assert comment_id

    # get it
    comments = character_garry.issue_comment_get_from_user(
        TEST_REPO, issue_id, character_garry.user_id
    )
    assert comment_id in comments.keys()

    # create reaction on it
    character_garry.issue_comment_reaction_create(
        TEST_REPO, issue_id, comment_id, ReactionType.HEART
    )

    # get reactions from it
    reactions = character_garry.issue_comment_reactions_get_from_user(
        TEST_REPO, issue_id, comment_id, character_garry.user_id
    )
    assert ReactionType.HEART in reactions

    # delete comment
    character_garry.issue_comment_delete(TEST_REPO, issue_id, comment_id)

    # check deleted
    comments = character_garry.issue_comment_get_from_user(
        TEST_REPO, issue_id, character_garry.user_id
    )
    assert comment_id not in comments.keys()

    # close it
    character_garry.issue_close(TEST_REPO, issue_id)

    # check it closed
    issue = character_garry.issue_get(TEST_REPO, issue_id)
    assert issue.state == "closed"
