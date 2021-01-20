""" Tests for Game module """

import pytest
from app.firebase_utils import db
from app.game import Game

# pylint: disable=redefined-outer-name
def test_bad_new():
    """ Errors caused by invaild new arguments """
    with pytest.raises(ValueError):
        Game.new("", "abc")

    with pytest.raises(ValueError):
        Game.new("abc", "")

    with pytest.raises(ValueError):
        Game.new("", "")


def test_invalid_init():
    """ Test invalid initialization with bad user """
    game = Game()

    with pytest.raises(ValueError):
        game.key


def test_second_creation(testing_game, random_id):
    """ Test second creation of game """
    fork_url = "url_" + random_id

    # assert url isn't what we'll set it to
    doc = db.collection("game").document(testing_game.key).get()
    assert doc.get("fork_url") != fork_url

    # make new game, this will update fork_url
    game = Game.new(testing_game.user, fork_url)

    # also check repr
    assert str(game)
    assert repr(game)

    # check it
    doc = db.collection("game").document(testing_game.key).get()
    assert doc.get("fork_url") == fork_url


def test_fail_find_user(random_user):
    """ Test failing to finding a game by user """

    game = Game.find_by_user(random_user)
    assert game is None


def test_find_user(testing_game):
    """ Test finding a game by user """

    user = testing_game.user

    game = Game.find_by_user(user)
    assert game.key == testing_game.key


def test_assign_uid(testing_game, random_id):
    """ Test assigning game to an UID """

    new_uid = "uid_" + random_id

    # assert uid isn't what we'll set it to
    doc = db.collection("game").document(testing_game.key).get()
    assert doc.get("user_uid") != new_uid

    testing_game.assign_to_uid(new_uid)

    # cehck it
    doc = db.collection("game").document(testing_game.key).get()
    assert doc.get("user_uid") == new_uid
